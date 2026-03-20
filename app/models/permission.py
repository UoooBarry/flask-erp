from flask import current_app


class Permission:
    def __init__(self, blueprint, endpoint, method):
        self.blueprint = blueprint
        self.endpoint = endpoint
        self.method = method

    @classmethod
    def all():
        permissions = []

        exclude_blueprints = {"auth", "static", "debug_toolbar"}

        for rule in current_app.url_map.iter_rules():
            endpoint = rule.endpoint
            exclude_methods = {"HEAD", "OPTIONS"}
            if "." in endpoint:
                bp_name = endpoint.split(".")[0]
                if bp_name not in exclude_blueprints and rule.methods:
                    permissions.extend(
                        Permission(bp_name, endpoint, method)
                        for method in rule.methods
                        if method not in exclude_methods
                    )

        return permissions
