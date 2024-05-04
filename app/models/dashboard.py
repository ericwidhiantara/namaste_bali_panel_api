from pydantic import BaseModel


class DashboardModel(BaseModel):
    total_unpaid: int
    total_paid: int
    total_canceled: int
    total_teams: int
    total_users: int
    total_orders: int
    total_destinations: int
