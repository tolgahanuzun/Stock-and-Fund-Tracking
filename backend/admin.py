from sqladmin import Admin, ModelView
from backend.models import User, Asset, Portfolio, PriceHistory
from backend.database import engine
from backend.i18n_utils import LazyString

def setup_admin(app):
    # templates_dir parametresini main.py'da veremiyoruz, burada Admin constructor'a verebiliriz.
    # Ancak setup_admin backend/main.py'dan çağrılıyor, orada templates_dir verilmesi daha doğru olabilir
    # veya burada direkt verebiliriz.
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

    admin.add_view(UserAdmin)
    admin.add_view(AssetAdmin)
    admin.add_view(PortfolioAdmin)
    admin.add_view(PriceHistoryAdmin)
