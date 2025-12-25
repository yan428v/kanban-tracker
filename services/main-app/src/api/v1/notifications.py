from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from models import Notification
from schemas.notification import CreateNotificationRequest, NotificationResponse, UpdateNotificationRequest
from services.notification import NotificationService, get_notification_service

router = APIRouter()

TASK_NOT_FOUND_MESSAGE = "Notification not found"


@router.get("/notifications", response_model=list[NotificationResponse])
async def list_notifications(
    skip: int = 0,
    limit: int = 100,
    service: NotificationService = Depends(get_notification_service),
):
    notifications = await service.get_many(skip=skip, limit=limit)
    return [notification_to_response(notification) for notification in notifications]


@router.get("/notifications/{notification_id}", response_model=NotificationResponse)
async def get_notification(
    notification_id: UUID,
    service: NotificationService = Depends(get_notification_service),
):
    notification = await service.get(notification_id)
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=TASK_NOT_FOUND_MESSAGE
        )
    return notification_to_response(notification)


@router.post("/notifications", response_model=NotificationResponse, status_code=status.HTTP_201_CREATED)
async def create_notification(
    notification_data: CreateNotificationRequest,
    service: NotificationService = Depends(get_notification_service),
):
    notification = await service.create(notification_data)
    return notification_to_response(notification)


@router.patch("/notifications/{notification_id}", response_model=NotificationResponse)
async def update_notification(
    notification_id: UUID,
    notification_data: UpdateNotificationRequest,
    service: NotificationService = Depends(get_notification_service),
):
    notification = await service.update(notification_id, notification_data)
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=TASK_NOT_FOUND_MESSAGE
        )
    return notification_to_response(notification)


@router.delete("/notifications/{notification_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_notification(
    notification_id: UUID,
    service: NotificationService = Depends(get_notification_service),
):
    result = await service.delete(notification_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=TASK_NOT_FOUND_MESSAGE
        )


def notification_to_response(notification: Notification) -> NotificationResponse:
    return NotificationResponse(
        message=notification.message,
        task_id=notification.task_id,
        id=notification.id,
        user_id=notification.user_id,
        created_at=notification.created_at,
        updated_at=notification.updated_at,
    )
