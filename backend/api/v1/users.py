import logging

from fastapi import APIRouter

log = logging.getLogger(__name__)


router = APIRouter(tags=["Пользователи"])
