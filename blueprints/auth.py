"""
Authentication Blueprint - Xử lý đăng ký, đăng nhập, đăng xuất.
"""
from flask import Blueprint, request, render_template, jsonify, session, redirect, url_for

from auth_utils import register_user, login_user, get_user_by_id

bp = Blueprint("auth", __name__)


@bp.route("/register", methods=["GET", "POST"])
def register():
    """Trang và xử lý đăng ký người dùng."""
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if password != confirm_password:
            return render_template(
                "register.html",
                error="Mật khẩu không khớp",
                username=username,
                email=email,
            )

        success, message = register_user(username, email, password)
        if success:
            return redirect(url_for("auth.login", registered="1"))
        return render_template(
            "register.html",
            error=message,
            username=username,
            email=email,
        )

    return render_template("register.html")


@bp.route("/login", methods=["GET", "POST"])
def login():
    """Trang và xử lý đăng nhập người dùng."""
    registered = request.args.get("registered") == "1"

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        success, message, user_data = login_user(username, password)
        if success:
            session["user_id"] = user_data["id"]
            session["username"] = user_data["username"]
            session["email"] = user_data["email"]
            session.permanent = True

            next_page = request.args.get("next", url_for("favorites.favorites"))
            return redirect(next_page)

        return render_template(
            "login.html",
            error=message,
            username=username,
            registered=registered,
        )

    return render_template("login.html", registered=registered)


@bp.route("/logout")
def logout():
    """Đăng xuất người dùng."""
    session.clear()
    return redirect(url_for("auth.login"))


@bp.route("/api/user")
def api_get_user():
    """API endpoint để lấy thông tin người dùng hiện tại."""
    if "user_id" not in session:
        return jsonify({"authenticated": False})

    user_data = get_user_by_id(session["user_id"])
    if user_data:
        return jsonify(
            {
                "authenticated": True,
                "user_id": user_data["id"],
                "username": user_data["username"],
                "email": user_data["email"],
            }
        )

    session.clear()
    return jsonify({"authenticated": False})

