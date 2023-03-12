#プロセスに対するcreate,edit,delete,process選択処理の定義

from flask import jsonify, Blueprint, request, render_template
from db_driver import dbDriver
import task

from sql_template import SQLTemplates as sql_temp

#プロセスのルーティング/<int:project_id>
bp = Blueprint('process', __name__, url_prefix="/<int:project_id>")
#タスクへのルーティング情報
bp.register_blueprint(task.bp)

#新規プロセス作成
@bp.route('/create', methods=['POST'])
def process_create(project_id):
    """
    新規にプロセスを作成する関数。
    ステータスは初期値となる。
    Method: POST
    jsonファイル例:
    {
        "process_name": "processのなまえ",
        "deadline":"2023-02-05"
    }
    """
    params = request.get_json()
    process_name = params["process_name"]
    deadline = params.get("deadline","0000-00-00")

    #dbDriverの生成
    regain_db_driver = dbDriver()
    
    try:
        #process生成SQL文
        process_insert_sql = sql_temp.PROCESS_INSERT_SQL.format(
            process_name = process_name,
            project_id = project_id,
            deadline = deadline
        )

        rows = regain_db_driver.sql_run(process_insert_sql)
        rows = regain_db_driver.sql_run("COMMIT")
    except Exception as e:
        print ('=== エラー内容 ===')
        print ('type:' + str(type(e)))
        print ('args:' + str(e.args))
        print ('e自身:' + str(e))
        return jsonify() # 本当はエラーページの表示をしたい

    #dbDriverのクローズと200OK返却
    regain_db_driver.db_close()
    return jsonify()



#既存プロセス編集
@bp.route('/edit', methods=['POST'])
def process_edit(project_id):
    """
    既存のプロジェクト情報を変更する関数。
    プロジェクト名の情報変更があった場合、その内容をDBに更新する。
    Method: POST
    jsonファイル例:
    {
        "process_id": 12345
        "process_name": "ほげほげ"
    }
    """

    # 処理開始
    print(f"処理開始: /{project_id}/edit")
    
    # dbDriverの生成
    regain_db_driver = dbDriver()

    ### プロセス名の更新があった場合、これをDBに反映（Update）する。
    try:
        # requestにより情報取得
        params = request.get_json()

        process_name, process_id = params["process_name"], params["process_id"]
        print(f"project_name: {process_name}, project_id: {process_id}")
        
        # HTTP200OKなどの結果を格納する数字
        result_num = 0

        # プロジェクト一覧更新SQL
        process_update_sql = sql_temp.PROCESS_UPDATE_SQL.format(
            process_name = process_name,
            process_id = process_id
        )

        rows = regain_db_driver.sql_run(process_update_sql)
        rows = regain_db_driver.sql_run("COMMIT")
        result_num = regain_db_driver.db_close()
    
    except:
        print("Something Failed...") # 本当はここでLoggerを使いたい

    # 処理終了
    print(f"処理終了: /{project_id}/edit")

    return jsonify()

#既存プロセス削除
@bp.route('/delete', methods=['DELETE'])
def process_delete(project_id):
    return jsonify()

#既存プロセス選択、タスク一覧表示
@bp.route('/<int:process_id>')
def task_get(project_id, process_id):
    """
    タスク一覧を表示。
    Method: GET
    """
    
    #dbDriverの生成
    regain_db_driver = dbDriver()

    try:
        #タスク一覧取得SQL
        task_select_sql = sql_temp.TASK_SELECT_SQL.format(
            process_id = process_id
        )
        tasks = regain_db_driver.sql_run(task_select_sql)
            
        #タスクステータス一覧取得
        status_names = regain_db_driver.sql_run(sql_temp.TASK_STATUS_NAME_SELECT_SQL)
            
        #優先度一覧取得
        priorities = regain_db_driver.sql_run(sql_temp.TASK_PRIORITY_SELECT_SQL)
    except Exception as e:
        print ('=== エラー内容 ===')
        print ('type:' + str(type(e)))
        print ('args:' + str(e.args))
        print ('e自身:' + str(e))
        return jsonify() # 本当はエラーページの表示をしたい

    #dbDriverのクローズと値返却
    regain_db_driver.db_close()
    # return jsonify(rows)
    return render_template('tasks.html', title='tasks', tasks=tasks, status_names = status_names, priorities = priorities)