import logging
from uuid import UUID
from typing import List
from starlette import status

from api.endpoints.models.credentials import PresentCredentialProtocolType

from sqlalchemy import select, desc
from sqlalchemy.sql.functions import func

from api.db.session import async_session
from api.db.models.v1.contact import Contact
from api.endpoints.models.v1.verifier import (
    VerifierPresentationItem,
    CreatePresentationRequestPayload,
    VerifierPresentationListParameters,
    VerifierPresentationStatusType,
    AcapyPresentProofStateType,
)

from api.db.models.v1.verifier_presentation import VerifierPresentation


logger = logging.getLogger(__name__)


def verifier_presentation_to_item(
    db_item: VerifierPresentation,
) -> VerifierPresentationItem:
    """VerifierPresentation to VerifierPresentationItem.

    Transform a VerifierPresentation Table record to a VerifierPresentationItem object.

    Args:
      db_item: The Traction database VerifierPresentation
      acapy: When True, populate the VerifierPresentationItem acapy field.

    Returns: The Traction VerifierPresentationItem

    """

    item = VerifierPresentationItem(
        **db_item.dict(),
    )
    return item


async def make_verifier_presentation(
    tenant_id: UUID,
    wallet_id: UUID,
    protocol: PresentCredentialProtocolType,
    payload: CreatePresentationRequestPayload,
) -> VerifierPresentationItem:

    db_contact = None
    async with async_session() as db:
        if payload.contact_id:
            db_contact = await Contact.get_by_id(db, tenant_id, payload.contact_id)
        elif payload.connection_id:
            db_contact = await Contact.get_by_connection_id(
                db, tenant_id, payload.connection_id
            )

    if not db_contact:
        raise Exception(
            code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            msg="no contact or connection found",
        )
    db_item = VerifierPresentation(
        tenant_id=tenant_id,
        contact_id=db_contact.contact_id,
        status=VerifierPresentationStatusType.PENDING,
        state=AcapyPresentProofStateType.PENDING,
        protocol=protocol,
        proof_request=payload.proof_request.dict(),
    )

    async with async_session() as db:
        db.add(db_item)
        await db.commit()

    return verifier_presentation_to_item(db_item)


async def list_presentation_requests(
    tenant_id: UUID,
    wallet_id: UUID,
    parameters: VerifierPresentationListParameters,
) -> List[VerifierPresentationItem]:

    limit = parameters.page_size
    skip = (parameters.page_num - 1) * limit

    filters = [
        VerifierPresentation.tenant_id == tenant_id,
    ]
    # handle simple filters
    # TODO: move this logic to central location
    for param, v in parameters.dict(exclude_none=True).items():
        logger.warning("filter parameter found: " + param)
        if param not in [
            "url",
            "page_num",
            "page_size",
            "acapy",
            "tenant_id",
            "tags",
        ]:  # special cases
            filters.append(getattr(VerifierPresentation, param) == v)

    if parameters.tags:
        _filter_tags = [x.strip() for x in parameters.tags.split(",")]
        filters.append(VerifierPresentation.tags.comparator.contains(_filter_tags))
    # build out a base query with all filters
    base_q = select(VerifierPresentation).filter(*filters)

    # get a count of ALL records matching our base query
    count_q = select([func.count()]).select_from(base_q)

    async with async_session() as db:

        count_q_rec = await db.execute(count_q)
        total_count = count_q_rec.scalar()

        # TODO: should we raise an exception if paging is invalid?
        # ie. is negative, or starts after available records

        # add in our paging and ordering to get the result set
        results_q = (
            base_q.limit(limit)
            .offset(skip)
            .order_by(desc(VerifierPresentation.updated_at))
        )

        results_q_recs = await db.execute(results_q)
        db_verifier_presentations = results_q_recs.scalars()

    items = []
    for db_verifier_presentation in db_verifier_presentations:
        item = verifier_presentation_to_item(db_verifier_presentation, parameters.acapy)
        items.append(item)

    return items, total_count
