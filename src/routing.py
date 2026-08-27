TEAM_BY_CATEGORY = {
    "Bug": "Engineering Support",
    "Feature Request": "Product Management",
    "How-To": "Product Support",
    "Performance": "Performance Support",
    "Billing": "Billing Support",
    "Integration": "Integrations Support",
    "Onboarding": "Onboarding Support",
    "Data Loss": "Data Recovery Support",
}


def get_responder_team(category):
    return TEAM_BY_CATEGORY.get(category, "General Support")