import ynab
import secrets_rs


class YNABClient:
    def __init__(self, access_token=None):
        """Initialize YNAB API Client."""
        self.configuration = ynab.Configuration(
            access_token=secrets_rs.ACCESS_TOKEN
        )

    def get_budget_by_id(self, budget_id):
        """Fetch detailed budget information by ID."""
        with ynab.ApiClient(self.configuration) as api_client:
            budgets_api = ynab.BudgetsApi(api_client)
            try:
                budget_response = budgets_api.get_budget_by_id(budget_id)
                return budget_response.data.budget
            except Exception as e:
                print(f"Error fetching budget: {e}")
                return None

    def get_budget_months(self, budget_id):
        """Fetch budget months for a given budget ID."""
        with ynab.ApiClient(self.configuration) as api_client:
            months_api = ynab.MonthsApi(api_client)
            try:
                months_response = months_api.get_budget_months(budget_id)
                return months_response.data.months
            except Exception as e:
                print(f"Error fetching budget months: {e}")
                return []

    def get_budgets(self):
        """Fetch the List of Budgets."""
        with ynab.ApiClient(self.configuration) as api_client:
            budgets_api = ynab.BudgetsApi(api_client)
            try:
                budgets_response = budgets_api.get_budgets()
                return budgets_response.data.budgets
            except Exception as e:
                print(f"Error fetching budgets: {e}")
                return []

    def get_accounts(self, budget_id):
        """Fetch accounts for a given budget ID."""
        with ynab.ApiClient(self.configuration) as api_client:
            accounts_api = ynab.AccountsApi(api_client)
            try:
                account_response = accounts_api.get_accounts(budget_id)
                return account_response.data.accounts  # List account objects
            except Exception as e:
                print(f"Error fetching accounts: {e}")
                return []

    def get_transactions(self, budget_id):
        """Fetch transactions for a given budget ID"""
        with ynab.ApiClient(self.configuration) as api_client:
            transactions_api = ynab.TransactionsApi(api_client)
            try:
                transact_response = transactions_api.get_transactions(budget_id)
                return transact_response.data.transactions
            except Exception as e:
                print('Exception when calling TransactionsApi->get_transactions: %s\n' % e)
                return []

    def get_categories(self, budget_id):
        with ynab.ApiClient(self.configuration) as api_client:
            categories_api = ynab.CategoriesApi(api_client)
            try:
                categories_response = categories_api.get_categories(budget_id)
                return categories_response.data.category_groups
            except Exception as e:
                print(f"Error fetching categories: {e}")
                return []

    def get_payees(self, budget_id):
        """Fetch payees for a given budget ID."""
        with ynab.ApiClient(self.configuration) as api_client:
            payees_api = ynab.PayeesApi(api_client)
            try:
                payees_response = payees_api.get_payees(budget_id)
                return payees_response.data.payees
            except Exception as e:
                print(f"Error fetching payees: {e}")
                return []
