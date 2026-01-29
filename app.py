from flask import Flask, jsonify
from flask_cors import CORS
import threading
import asyncio

from test_agent_manager import get_test_agent

# 创建Flask应用
app = Flask(__name__)
test_agent = get_test_agent()
# 启用CORS
CORS(app)

# 注册Swagger UI蓝图
# 注册蓝图
# app.register_blueprint(test_case_bp, url_prefix='/api/test-cases')
# app.register_blueprint(test_case_step_bp, url_prefix='/api/test-case-steps')
# app.register_blueprint(test_case_result_bp, url_prefix='/api/test-case-results')

# 错误处理
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'message': 'Resource not found',
        'error': 404
    }), 404

@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        'success': False,
        'message': 'Bad request',
        'error': 400
    }), 400

@app.errorhandler(500)
def server_error(error):
    return jsonify({
        'success': False,
        'message': 'Internal server error',
        'error': 500
    }), 500

# 根路由
@app.route('/')
def index():
    return jsonify({
        'success': True,
        'message': 'Welcome to the Test Management API',
        'version': '1.0.0'
    })

@app.route('/add-queue/<int:test_case_id>', methods=['GET'])
def add_queue(test_case_id:int):
    test_agent.add_to_test_queue(test_case_id)
    return jsonify({
        'success': True,
        'message': f'测试用例{test_case_id}成功入列',
    })

@app.route('/clear-queue/<int:test_case_id>', methods=['GET'])
def clear_queue():
    test_agent.clear_test_queue()
    return jsonify({
        'success': True,
        'message': f'测试用例队列已清空',
    })

# # 提供Swagger JSON文件
# @app.route('/static/swagger.json')
# def swagger_json():
#     return send_from_directory('static', 'swagger.json')
#
# 创建asyncio事件循环运行函数

def run_async_task():
    asyncio.run(test_agent.run())

# 启动异步任务线程
def start_async_task():
    """启动异步任务线程"""
    thread = threading.Thread(target=run_async_task, daemon=True)
    thread.start()
    print("Async task thread started")
    return thread

# 应用启动时初始化代码
# 创建一个全局变量来存储异步线程
async_thread = None


# 在应用启动时自动启动异步任务
def start_background_task():
    """启动后台异步任务"""
    global async_thread
    if async_thread is None or not async_thread.is_alive():
        print("Starting background task...")
        async_thread = start_async_task()
        return True
    else:
        print("Background task is already running")
        return False

# 创建一个启动函数
def start_app():
    """启动应用并初始化异步任务"""
    # 在生产模式下自动启动异步任务

    start_background_task()
    return app

# 如果直接运行这个文件，启动应用
if __name__ == '__main__':
    start_app()
    app.run(debug=True, host='0.0.0.0', port=5001)
