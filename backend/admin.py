from sqladmin import Admin, ModelView, BaseView, expose
from backend.models import User, Asset, Portfolio, PriceHistory
from backend.database import engine
from backend.i18n_utils import LazyString
from sqlalchemy.orm import Session
from sqlalchemy import func

def setup_admin(app):
    admin = Admin(app, engine, templates_dir="backend/templates")

    class UserAdmin(ModelView, model=User):
        name = LazyString("User")
        name_plural = LazyString("Users")
        column_list = [User.id, User.username, User.full_name]
        column_labels = {
            User.id: LazyString("ID"),
            User.username: LazyString("Username"),
            User.full_name: LazyString("Full Name")
        }

    class AssetAdmin(ModelView, model=Asset):
        name = LazyString("Asset")
        name_plural = LazyString("Assets")
        column_list = [Asset.id, Asset.code, Asset.name, Asset.type]
        column_labels = {
            Asset.id: LazyString("ID"),
            Asset.code: LazyString("Code"),
            Asset.name: LazyString("Name"),
            Asset.type: LazyString("Type")
        }

    class PortfolioAdmin(ModelView, model=Portfolio):
        name = LazyString("Portfolio")
        name_plural = LazyString("Portfolios")
        column_list = [Portfolio.id, Portfolio.user_id, Portfolio.asset_id, Portfolio.quantity, Portfolio.average_cost]
        column_labels = {
            Portfolio.id: LazyString("ID"),
            Portfolio.user_id: LazyString("User ID"),
            Portfolio.asset_id: LazyString("Asset ID"),
            Portfolio.quantity: LazyString("Quantity"),
            Portfolio.average_cost: LazyString("Avg Cost")
        }

    class PriceHistoryAdmin(ModelView, model=PriceHistory):
        name = LazyString("Price History")
        name_plural = LazyString("Price Histories")
        column_list = [PriceHistory.id, PriceHistory.asset_id, PriceHistory.date, PriceHistory.price]
        column_sortable_list = [PriceHistory.date]
        column_labels = {
            PriceHistory.id: LazyString("ID"),
            PriceHistory.asset_id: LazyString("Asset ID"),
            PriceHistory.date: LazyString("Date"),
            PriceHistory.price: LazyString("Price")
        }

    class LatestPricesView(BaseView):
        name = "Latest Prices"
        icon = "fa-solid fa-chart-line"

        @expose("/latest-prices", methods=["GET"])
        async def latest_prices(self, request):
            with Session(engine) as db:
                # Subquery to find the max date for each asset
                subquery = db.query(
                    PriceHistory.asset_id,
                    func.max(PriceHistory.date).label('max_date')
                ).group_by(PriceHistory.asset_id).subquery()

                results = db.query(
                    Asset.code,
                    Asset.name,
                    Asset.type,
                    PriceHistory.price,
                    PriceHistory.date
                ).join(PriceHistory, Asset.id == PriceHistory.asset_id)\
                 .join(subquery, (PriceHistory.asset_id == subquery.c.asset_id) & (PriceHistory.date == subquery.c.max_date))\
                 .order_by(PriceHistory.date.desc())\
                 .limit(20)\
                 .all()

            return await self.templates.TemplateResponse(
                request, 
                "prices.html", 
                context={"prices": results}
            )

    admin.add_view(UserAdmin)
    admin.add_view(AssetAdmin)
    admin.add_view(PortfolioAdmin)
    admin.add_view(PriceHistoryAdmin)
    admin.add_view(LatestPricesView)
