from app import create_app, db
from app.models.user import User
from app.models.role import Role


def seed_database():
    app = create_app()

    with app.app_context():
        admin_role = Role.query.filter_by(name="admin").first()

        if not admin_role:
            admin_role = Role(name="admin")
            db.session.add(admin_role)
            db.session.commit()
            print("Admin role created successfully")
        else:
            print("Admin role already exists")

        admin_user = User.query.filter_by(username="admin").first()

        if not admin_user:
            admin_user = User(username="admin")
            # Modify when production
            admin_user.password = "defaultadmin"
            db.session.add(admin_user)
            db.session.commit()
            admin_role.users.append(admin_user)
            db.session.commit()
            print("Admin user created successfully with admin role")
        else:
            if admin_user not in admin_role.users:
                admin_role.users.append(admin_user)
                db.session.commit()
                print("Admin role assigned to existing admin user")
            else:
                print("Admin user with admin role already exists")


if __name__ == "__main__":
    seed_database()

