from config.database import get_db
from dal.repositories.role_repository import RoleRepository
from dal.repositories.user_repository import UserRepository
from dal.repositories.user_role_repository import UserRoleRepository


def create_default_roles():
    db = next(get_db())

    try:
        # 创建角色仓储
        role_repo = RoleRepository(db)

        # 创建默认角色
        customer_role = role_repo.create({"role_name": "customer", "description": "Regular bank customer"})
        staff_role = role_repo.create({"role_name": "bank_staff", "description": "Bank employee"})
        admin_role = role_repo.create({"role_name": "system_admin", "description": "System administrator"})

        print(
            f"Created roles: customer({customer_role.role_id}), staff({staff_role.role_id}), admin({admin_role.role_id})")

        # 创建用户角色仓储
        user_role_repo = UserRoleRepository(db)

        # 给所有现有用户分配客户角色
        user_repo = UserRepository(db)
        users = user_repo.get_all()

        for user in users:
            user_role_repo.assign_role(user.user_id, customer_role.role_id)
            print(f"Assigned customer role to user: {user.username}")

        # 可以为特定用户分配管理员角色
        # 比如第一个用户作为管理员
        if users:
            user_role_repo.assign_role(users[0].user_id, admin_role.role_id)
            print(f"Assigned admin role to user: {users[0].username}")

        print("Default roles created successfully")

    except Exception as e:
        print(f"Error creating default roles: {str(e)}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    create_default_roles()