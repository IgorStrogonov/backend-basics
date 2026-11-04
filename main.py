from datetime import datetime
from enum import Enum
from typing import Optional

from fastapi import FastAPI, Depends, HTTPException, Query, status, Response
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str=""
    default_page_size: int = 1
    max_page_size: int = 1
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

def get_settings() -> Settings:
    return Settings()

class DrinkSize(str, Enum):
    small = "small"
    medium = "medium"
    large = "large"

class OrderStatus(str, Enum):
    pending = "pending"
    ready = "ready"
    completed = "completed"
    cancelled = "cancelled"

class OrderCreate(BaseModel):
    drink: str = Field(min_length=1, description="Название напитка из меню", examples=["Латте"]) 
    size: DrinkSize = Field(description="Размер", examples=["medium"])
    quantity: int = Field(gt=0, description="Количество", examples=[2])
    customer_name: Optional[str] = Field(None, description="Имя клиента", examples=["Ирина"])

class OrderUpdate(BaseModel):
    drink: Optional[str] = Field(None, min_length=1, description="Название напитка из меню", examples=["Латте"])
    size: Optional[DrinkSize] = Field(None, description="Размер", examples=["medium"])
    quantity: Optional[int] = Field(None, gt=0, description="Количество", examples=[2])
    customer_name: Optional[str] = Field(None, description="Имя клиента", examples=["Ирина"])
    status: Optional[OrderStatus] = Field(None, description="Статус заказа", examples=["ready"])

class OrderResponse(BaseModel):
    id: int
    drink: str
    size: DrinkSize
    quantity: int
    customer_name: Optional[str]
    status: OrderStatus
    created_at: datetime

app = FastAPI(
    title="Coffee Shop Orders API",
    description="Сервис учёта заказов для кофейни. Позволяет создавать, просматривать, изменять и удалять заказы.",
    version="1.0.0",
)

orders: list[dict] = []
order_id_cnt = 1

@app.get("/", tags=["Сервис"], summary="Приветственное сообщение")
def read_root():
    return {"message": "Добро пожаловать в сервис учёта заказов кофейни"}

@app.get("/info", tags=["Сервис"], summary="Информация о сервисе")
def get_info(settings: Settings = Depends(get_settings)):
    return {
        "app_name": settings.app_name,
        "current_orders_count": len(orders),
    }

@app.post("/orders", response_model=OrderResponse, status_code=status.HTTP_201_CREATED, tags=["Заказы"], summary="Создать новый заказ")
def create_order(order: OrderCreate):
    global order_id_cnt
    new_order = {
        "id": order_id_cnt,
        "drink": order.drink,
        "size": order.size,
        "quantity": order.quantity,
        "customer_name": order.customer_name,
        "status": OrderStatus.pending,
        "created_at": datetime.now(),
    }
    orders.append(new_order)
    order_id_cnt += 1
    return new_order

@app.get("/orders", response_model=list[OrderResponse], tags=["Заказы"], summary="Получить список заказов")
def list_orders(
    status_filter: Optional[OrderStatus] = Query(None, alias="status", description="Фильтр по статусу заказа"), 
    limit: int = Query(10, gt=0, le=100, description="Количество заказов на странице"), 
    offset: int = Query(0, ge=0, description="Смещение для пагинации")
):
    result = orders
    if status_filter is not None:
        result = [i for i in result if i["status"] == status_filter]
    return result[offset : offset+limit]

@app.get("/orders/{order_id}", response_model=OrderResponse, tags=["Заказы"], summary="Получить заказ по ID")
def get_order(order_id: int):
    for order in orders:
        if order["id"] == order_id:
            return order
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Заказ не найден")

@app.patch("/orders/{order_id}", response_model=OrderResponse, status_code=status.HTTP_200_OK, tags=["Заказы"], summary="Частично обновить заказ")
def update_order(order_id: int, order_update: OrderUpdate):
    for order in orders:
        if order["id"] == order_id:
            update_data = order_update.model_dump(exclude_unset=True)
            order.update(update_data)
            return order
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Заказ не найден")

@app.delete("/orders/{order_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Заказы"], summary="Отменить (удалить) заказ")
def delete_order(order_id: int):
    global orders
    for i, order in enumerate(orders):
        if order["id"] == order_id:
            orders.pop(i)
            return Response(status_code=status.HTTP_204_NO_CONTENT)
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Заказ не найден")