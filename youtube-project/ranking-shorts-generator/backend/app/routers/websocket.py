"""
WebSocket Router for Real-time Communication
Based on design doc: docs/07-backend-api.md
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, List
import json
import logging
import asyncio
from celery_app import celery_app

logger = logging.getLogger(__name__)

router = APIRouter()


class ConnectionManager:
    """WebSocket 연결 관리 클래스"""

    def __init__(self):
        # {client_id: WebSocket}
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, client_id: str, websocket: WebSocket):
        """클라이언트 연결"""
        await websocket.accept()
        self.active_connections[client_id] = websocket
        logger.info(f"Client connected: {client_id}, Total: {len(self.active_connections)}")

    def disconnect(self, client_id: str):
        """클라이언트 연결 해제"""
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            logger.info(
                f"Client disconnected: {client_id}, Total: {len(self.active_connections)}"
            )

    async def send_message(self, client_id: str, message: dict):
        """특정 클라이언트에게 메시지 전송"""
        if client_id in self.active_connections:
            try:
                await self.active_connections[client_id].send_json(message)
            except Exception as e:
                logger.error(f"Failed to send message to {client_id}: {e}")
                self.disconnect(client_id)

    async def broadcast(self, message: dict):
        """모든 클라이언트에게 메시지 브로드캐스트"""
        disconnected = []
        for client_id, connection in self.active_connections.items():
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Failed to broadcast to {client_id}: {e}")
                disconnected.append(client_id)

        # 연결 실패한 클라이언트 제거
        for client_id in disconnected:
            self.disconnect(client_id)


# ConnectionManager 인스턴스
manager = ConnectionManager()


@router.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """
    WebSocket 연결 엔드포인트

    Args:
        websocket: WebSocket 연결
        client_id: 클라이언트 고유 ID

    기능:
        - 실시간 진행 상황 업데이트
        - Celery 작업 상태 모니터링
        - 양방향 메시지 통신
    """
    await manager.connect(client_id, websocket)

    try:
        while True:
            # 클라이언트로부터 메시지 수신
            data = await websocket.receive_text()
            message = json.loads(data)

            message_type = message.get("type")

            if message_type == "ping":
                # 핑 응답
                await manager.send_message(
                    client_id, {"type": "pong", "timestamp": message.get("timestamp")}
                )

            elif message_type == "subscribe_task":
                # Celery 작업 구독
                task_id = message.get("task_id")
                if task_id:
                    # 백그라운드에서 작업 상태 모니터링
                    asyncio.create_task(monitor_task(client_id, task_id))

            elif message_type == "unsubscribe_task":
                # 작업 구독 해제 (추후 구현)
                pass

            else:
                # 에코 (디버깅용)
                await manager.send_message(
                    client_id, {"type": "echo", "message": message.get("message")}
                )

    except WebSocketDisconnect:
        manager.disconnect(client_id)
        logger.info(f"Client {client_id} disconnected normally")

    except Exception as e:
        logger.error(f"WebSocket error for {client_id}: {e}")
        manager.disconnect(client_id)


async def monitor_task(client_id: str, task_id: str):
    """
    Celery 작업 상태를 실시간으로 모니터링하고 클라이언트에게 전송

    Args:
        client_id: 클라이언트 ID
        task_id: Celery 작업 ID
    """
    logger.info(f"Monitoring task {task_id} for client {client_id}")

    while True:
        try:
            # Celery 작업 상태 조회
            task = celery_app.AsyncResult(task_id)
            state = task.state

            # 진행 상황 메시지 전송
            message = {
                "type": "task_update",
                "task_id": task_id,
                "state": state,
                "info": task.info if task.info else {},
            }

            await manager.send_message(client_id, message)

            # 완료 또는 실패 시 모니터링 종료
            if state in ["SUCCESS", "FAILURE", "REVOKED"]:
                logger.info(f"Task {task_id} finished with state: {state}")
                break

            # 1초마다 체크
            await asyncio.sleep(1)

        except Exception as e:
            logger.error(f"Error monitoring task {task_id}: {e}")
            break


@router.websocket("/ws/broadcast")
async def broadcast_websocket(websocket: WebSocket):
    """
    브로드캐스트 전용 WebSocket 엔드포인트
    (관리자가 모든 클라이언트에게 메시지 전송)
    """
    await websocket.accept()

    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)

            # 모든 클라이언트에게 브로드캐스트
            await manager.broadcast(message)

    except WebSocketDisconnect:
        logger.info("Broadcast client disconnected")
    except Exception as e:
        logger.error(f"Broadcast WebSocket error: {e}")


# 유틸리티 함수 (다른 모듈에서 사용 가능)
async def notify_client(client_id: str, notification: dict):
    """
    특정 클라이언트에게 알림 전송

    Args:
        client_id: 클라이언트 ID
        notification: 알림 메시지
    """
    await manager.send_message(client_id, notification)


async def notify_all(notification: dict):
    """
    모든 클라이언트에게 알림 전송

    Args:
        notification: 알림 메시지
    """
    await manager.broadcast(notification)
