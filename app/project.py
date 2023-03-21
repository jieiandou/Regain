#プロジェクトに対するcreate,edit,delete,project選択処理の定義

from flask import jsonify, Blueprint, request, render_template
from db_driver import dbDriver
import process
import datetime
import math
import logging

from sql_template import SQLTemplates as sql_temp

#プロジェクトのルーティング/
bp = Blueprint('project', __name__, url_prefix="/")
#プロセスへのルーティング情報
bp.register_blueprint(process.bp)

#新規プロジェクト作成
@bp.route('/create', methods=['POST'])
def project_create() -> int:
    """
    新規にプロジェクトを作成する関数。
    Method: POST
    jsonファイル例:
    {
        "project_name": "projectのなまえ"
    }

    Returns:
        int: 200 (OK) or 500 (NG)
    """
    params = request.get_json()
    project_name = params["project_name"]

    #dbDriverの生成
    regain_db_driver = dbDriver()
    
    try:
        #project生成SQL文
        project_insert_sql =  sql_temp.PROJECT_INSERT_SQL.format(project_name = project_name)
        rows = regain_db_driver.sql_run(project_insert_sql)
        rows = regain_db_driver.sql_run("COMMIT")
        regain_db_driver.db_close()

        # 200 (OK)
        result_num = 200
        return f"Project with project_name: {project_name} created.", result_num
    
    except Exception as e:
        print("Error creating project: {e}") # 本当はここでLoggerを使いたい

        # 500 (NG)
        result_num = 500
        return f"Error creating project with project_name: {project_name}.\nError: {str(e)}", result_num

#既存プロジェクト編集
@bp.route('/edit', methods=['POST'])
def project_edit() -> int:
    """
    既存のプロジェクト情報を変更する関数。
    プロジェクト名の情報変更があった場合、その内容をDBに更新する。
    Method: POST
    jsonファイル例:
    {
        "project_id": 12345
        "project_name": "ほげほげ"
    }

    Returns:
        int: 200(OK) or 500(NG)
    """

    # 処理開始
    print("処理開始: /edit")
    
    # dbDriverの生成
    regain_db_driver = dbDriver()

    ### プロジェクト名の更新があった場合、これをDBに反映（Update）する。
    try:
        # requestにより情報取得
        params = request.get_json()

        project_name = params["project_name"]
        project_id = params["project_id"]
        print(f"project_name: {project_name}, project_id: {project_id}")

        # プロジェクト一覧更新SQL
        project_update_sql = sql_temp.PROJECT_UPDATE_SQL.format(
            project_name = project_name,
            project_id = project_id
        )
        rows = regain_db_driver.sql_run(project_update_sql)
        rows = regain_db_driver.sql_run("COMMIT")

        regain_db_driver.db_close()

        # 200 (OK)
        result_num = 200
        return f"Project with project_id: {project_id} edited.", result_num
    
    except Exception as e:
        print("Error editing project: {e}") # 本当はここでLoggerを使いたい

        # 500 (NG)
        result_num = 500
        return f"Error editing project with project_id: {project_id}.\nError: {str(e)}", result_num


#既存プロジェクト削除
@bp.route('/delete', methods=['DELETE'])
def project_delete() -> int:
    """
    既存プロジェクト削除処理。
    受け取ったproject_idに対応するプロジェクトを削除する。

    jsonファイル例:
    {
        "project_id": 12345
    }

    Returns:
        int: 200(OK) or 500(NG)
    """
    # 処理開始
    print("処理開始: /delete")
    
    # dbDriverの生成
    regain_db_driver = dbDriver()

    ### プロジェクト名の更新があった場合、これをDBに反映（Update）する。
    try:
        # requestにより情報取得
        params = request.get_json()
        print(f"params: {params}")

        project_id = params["project_id"]
        print(f"project_id: {project_id}")

        # プロジェクト一覧更新SQL
        project_delete_sql = sql_temp.PROJECT_DELETE_SQL.format(project_id=project_id)
        rows = regain_db_driver.sql_run(project_delete_sql)
        rows = regain_db_driver.sql_run("COMMIT")

        regain_db_driver.db_close()

        # 200 (OK)
        result_num = 200
        return f"Project with project_id: {project_id} deleted.", result_num

    except Exception as e:
        print(f"Error deleting project: {e}") # 本当はここでLoggerを使いたい

        # 500 (NG)
        result_num = 500
        return f"Error deleting project with project_id: {project_id}.\nError: {str(e)}", result_num

#既存プロジェクト選択、プロセス一覧表示
@bp.route('/<int:project_id>')
def process_get(project_id:int) -> str:
    """
    プロセス一覧を表示する関数。
    Method: GET

    Args:
        project_id (int): 各プロジェクトに割り振られたID

    Returns:
        str: htmlテンプレート (processes.html)
    """
    
    #dbDriverの生成
    regain_db_driver = dbDriver()
    

    try:
        #プロジェクト名取得
        project_name = regain_db_driver.sql_run(sql_temp.PROJECT_NAME_SELECT_SQL.format(project_id = project_id))[0]["project_name"]

        #本日の日付取得
        now = datetime.datetime.now()
        now_str = now.strftime("%Y-%m-%d")
        #本日の作業時間取得SQL
        process_commit_time_sum_sql = sql_temp.PROCESS_COMMIT_TIME_SUM_SELECT_SQL.format(commit_date = now_str)
        #プロセス一覧取得SQL
        process_list_sql = sql_temp.PROCESS_SELECT_SQL.format(
            process_commit_time_sum = process_commit_time_sum_sql,
            process_estimated_time_sum = sql_temp.PROCESS_ESTIMATED_TIME_SUM_SELECT_SQL,
            project_id = project_id
        )
        processes = regain_db_driver.sql_run(process_list_sql)

        #予測日数を計算
        for one_process in processes:
            one_process["worktime_today"] = one_process["today_commit_time"]
        #     #過去の作業記録がないプロセスのpredict_timeは-1
        #     if(one_process["passed_date"] == 0 or (one_process["today_commit_time"] > 0 and one_process["passed_date"] == 1)) :
        #         one_process["predict_time"] = -1
        #         continue
                
        #     #本日の作業分は除外して作業時間/日を計算する
        #     #予測時間への必要日数を計算したのち、作業日数を引いて残り予測日数を出す
        #     if(one_process["today_commit_time"] > 0):
        #         passed_time_par_day = (one_process["passed_time_sec"] - one_process["today_commit_time"]) / (one_process["passed_date"] - 1)
        #         required_day = one_process["estimated_time_sec"] / passed_time_par_day
        #         predict_time = required_day - (one_process["passed_date"] - 1)
        #     else:
        #         passed_time_par_day = one_process["passed_time_sec"]/ one_process["passed_date"]
        #         required_day = one_process["estimated_time_sec"] / passed_time_par_day
        #         predict_time = required_day - one_process["passed_date"]
        #     one_process["predict_time"] = math.ceil(predict_time)
            
        #プロセスステータス一覧取得SQL
        status_names = regain_db_driver.sql_run(sql_temp.PROCESS_STATUS_NAME_SELECT_SQL)

        regain_db_driver.db_close()
        return render_template('processes.html', title='processes', processes=processes, status_names = status_names, project_id = project_id, project_name = project_name)
    
    except Exception as e:
        print("Error getting process: {e}") # 本当はここでLoggerを使いたい

        # 500 (NG)
        result_num = 500
        logging.error(str(e))
        return "Error getting process with project_id: {project_id}.\nError: {error}".format(
            project_id=project_id, error=str(e)
        ), result_num
