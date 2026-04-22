from pydantic import BaseModel, Field, field_validator


class CartItemInput(BaseModel):
    item_id: str = Field(..., min_length=1)
    quantity: int = Field(..., ge=0, le=20)


class OptimizeRequest(BaseModel):
    budget: int = Field(..., ge=1)
    cart_items: list[CartItemInput]
    include_visualization: bool = True

    @field_validator("cart_items")
    @classmethod
    def non_empty_cart(cls, values: list[CartItemInput]) -> list[CartItemInput]:
        if not any(item.quantity > 0 for item in values):
            raise ValueError("At least one item quantity must be greater than zero.")
        return values
