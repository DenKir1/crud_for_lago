from fastapi import APIRouter
from app.utils.lago import create_user_lago, top_up_wallet, get_wallet, withdraw_form_wallet

lago_crud_router = APIRouter(prefix="/users", tags=["lago_crud"])


@lago_crud_router.post("/", summary="Create new user",)  # response_model=UserPydantic)
async def create_user(user_id: str):
    user = create_user_lago(user_id)
    return user


@lago_crud_router.post("/withdraw", summary="Pay from your account ",)
async def make_payment(user_id: str, amount: int, type_: str):
    wallet = withdraw_form_wallet(user_id, amount, type_)
    return wallet


@lago_crud_router.get("/balance", summary="User's balance ", )
async def make_balance(user_id: str):
    wallet = get_wallet(user_id)
    return wallet


@lago_crud_router.post("/deposit", summary="Add to your account ", )
async def make_deposit(user_id: str, amount: int):
    wallet = top_up_wallet(user_id, amount)
    return wallet
