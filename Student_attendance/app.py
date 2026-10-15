from flask import Flask, render_template
from config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Import blueprints
    from routes.auth_routes import auth_bp
    from routes.student_routes import student_bp
    from routes.faculty_routes import faculty_bp
    from routes.attendance_routes import attendance_bp

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(student_bp, url_prefix='/student')
    app.register_blueprint(faculty_bp, url_prefix='/faculty')
    app.register_blueprint(attendance_bp, url_prefix='/faculty/attendance')

    @app.route('/')
    def index():
        return render_template('auth/login.html')

    # Global error handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(403)
    def forbidden(e):
        return render_template('errors/403.html'), 403

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('errors/500.html'), 500

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
