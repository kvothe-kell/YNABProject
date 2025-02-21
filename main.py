import ynab
import secrets

configuration = ynab.Configuration(
    access_token=secrets.ACCESS_TOKEN
)

with ynab.ApiClient(configuration) as api_client:
    budgets_api = ynab.BudgetsApi(api_client)
    budgets_response = budgets_api.get_budgets()
    budgets = budgets_response.data.budgets

    for budget in budgets:
        print(budget.name)
