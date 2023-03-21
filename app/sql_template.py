# SQLのテンプレートを格納する部分

class SQLTemplates():
    ##########################
    ###### UPDATE(EDIT) ######
    ##########################
    
    PROJECT_UPDATE_SQL = """
    UPDATE
        projects
    SET
        project_name = '{project_name}'
    WHERE
        project_id = {project_id}
    """
    
    PROCESS_UPDATE_SQL = """
    UPDATE
        processes
    SET
        process_name = '{process_name}',
        status_id = {status_id},
        deadline = CAST('{deadline}' as DATE)
    WHERE
        process_id = {process_id}
    """

    TASK_UPDATE_SQL = """
    UPDATE
        tasks
    SET
        task_name = '{task_name}',
        status_id = {status_id},
        priority_id = {priority_id},
        estimated_time = CAST('{estimated_time}' as TIME),
        deadline = CAST('{deadline}' as DATE)
    WHERE
        task_id = {task_id}  
    """

    TIMER_UPDATE_SQL = """
    INSERT INTO
        commits (commit_date, commit_time, task_id)
    VALUES
        (CAST('{commit_date}' as DATE), CAST('{commit_time}' as TIME), {task_id})
    ON DUPLICATE KEY UPDATE
        commit_time = '{commit_time}'
    """
    ####################
    ###### INSERT ######
    ####################

    PROJECT_INSERT_SQL= """
    INSERT INTO
        projects (project_name)
    VALUES
        ('{project_name}')
    """

    PROCESS_INSERT_SQL= """
    INSERT INTO
        processes (process_name, project_id, deadline)
    VALUES
        ('{process_name}', {project_id}, CAST('{deadline}' as DATE))
    """

    TASK_INSERT_SQL= """
    INSERT INTO
        tasks (task_name, process_id, priority_id, estimated_time, deadline)
    VALUES
        ('{task_name}', {process_id}, {priority_id}, CAST('{estimated_time}' as TIME), CAST('{deadline}' as DATE))
    """

    ##################
    ###### TIME ######
    ##################

    PROJECT_ESTIMATED_TIME_SUM_SELECT_SQL = """
    SELECT
        projects.project_id,
        DATE_FORMAT(SEC_TO_TIME(IFNULL(SUM(TIME_TO_SEC(estimated_time)), 0)),'%k:%i') as estimated_time
    FROM
        projects
        LEFT JOIN processes
            ON projects.project_id = processes.project_id
        LEFT JOIN tasks
            ON processes.process_id = tasks.process_id
    GROUP BY
        project_id
    """

    PROCESS_COMMIT_TIME_SUM_SELECT_SQL="""
    SELECT
        processes.process_id,
        DATE_FORMAT(SEC_TO_TIME(IFNULL(SUM(TIME_TO_SEC(commit_time)), 0)), '%k:%i')  as today_commit_time
    FROM
        processes
        LEFT JOIN tasks
            ON processes.process_id = tasks.process_id
        LEFT JOIN commits
            ON tasks.task_id = commits.task_id
    WHERE
        commit_date = '{commit_date}'
    GROUP BY
        process_id
    """
    
    PROJECT_SELECT_SQL="""
    SELECT
        projects.project_id,
        project_name,
        estimated_time_sum.estimated_time as estimated_time,
        DATE_FORMAT(SEC_TO_TIME(IFNULL(SUM(TIME_TO_SEC(commit_time)), 0)),'%k:%i') as passed_time
    FROM
        projects
        LEFT JOIN processes
            ON projects.project_id = processes.project_id
        LEFT JOIN tasks
            ON processes.process_id = tasks.process_id
        LEFT JOIN commits
            ON tasks.task_id = commits.task_id
        LEFT JOIN ({project_estimated_time_sum}) as estimated_time_sum
            ON projects.project_id = estimated_time_sum.project_id
    GROUP BY
        project_id
    """

    PROJECT_NAME_SELECT_SQL="""
    SELECT
        project_name
    FROM
        projects
    WHERE
        project_id = {project_id}
    """

    PROCESS_ESTIMATED_TIME_SUM_SELECT_SQL="""
    SELECT
        processes.process_id,
        DATE_FORMAT(SEC_TO_TIME(IFNULL(SUM(TIME_TO_SEC(estimated_time)), 0)),'%k:%i') as estimated_time,
        IFNULL(SUM(TIME_TO_SEC(estimated_time)), 0) as estimated_time_sec
    FROM
        processes
        LEFT JOIN tasks
            ON processes.process_id = tasks.process_id
    GROUP BY
        process_id
    """

    PROCESS_SELECT_SQL="""
    SELECT
        processes.process_id,
        process_name,
        estimated_time_sum.estimated_time as estimated_time,
        estimated_time_sum.estimated_time_sec as estimated_time_sec,
        DATE_FORMAT(processes.deadline,'%c/%e') as deadline,
        DATE_FORMAT(SEC_TO_TIME(IFNULL(SUM(TIME_TO_SEC(commit_time)), 0)),'%k:%i') as passed_time,
        IFNULL(SUM(TIME_TO_SEC(commit_time)), 0) as passed_time_sec,
        COUNT(DISTINCT commit_date) as passed_date,
        IFNULL(today_commit_time, '0:00') as today_commit_time,
        status_name
    FROM
        processes
        LEFT JOIN tasks
            ON processes.process_id = tasks.process_id
        LEFT JOIN commits
            ON tasks.task_id = commits.task_id
        LEFT JOIN ({process_commit_time_sum}) as today_commit_time_table
            ON processes.process_id = today_commit_time_table.process_id
        LEFT JOIN process_statuses
            ON processes.status_id = process_statuses.status_id
        LEFT JOIN ({process_estimated_time_sum}) as estimated_time_sum
            ON processes.process_id = estimated_time_sum.process_id
    WHERE
        processes.project_id = {project_id}
    GROUP BY
        process_id
    """

    PROCESS_STATUS_NAME_SELECT_SQL = """
    SELECT
        status_id, status_name
    FROM
        process_statuses
    """

    TASK_SELECT_SQL="""
    SELECT
        tasks.task_id,
        task_name,
        DATE_FORMAT(estimated_time,'%k:%i') as estimated_time,
        DATE_FORMAT(deadline,'%c/%e') as deadline,
        DATE_FORMAT(sec_to_time(IFNULL(sum(time_to_sec(commit_time)),0)),'%k:%i') as passed_time,
        status_name,
        priority_name
    FROM 
        tasks
        left join commits
            on tasks.task_id = commits.task_id
        left join task_statuses
            on tasks.status_id = task_statuses.status_id
        left join priorities
            on tasks.priority_id = priorities.priority_id
    WHERE 
        process_id = {process_id}
    GROUP BY
        task_id
    """

    PROJECT_NAME_SELECT_SQL="""
    SELECT
        project_name
    FROM
        projects
    WHERE
        project_id = {project_id}
    """

    PROCESS_NAME_SELECT_SQL="""
    SELECT
        process_name
    FROM
        processes
    WHERE
        process_id = {process_id}
    """

    TASK_STATUS_NAME_SELECT_SQL = """
    SELECT
        status_id, status_name
    FROM
        task_statuses
    """

    TASK_PRIORITY_SELECT_SQL = """
    SELECT
        priority_id, priority_name
    FROM
        priorities
    """

    TIMAR_NAME_SELECT_SQL = """
    SELECT
        task_name
    FROM
        tasks
    WHERE 
        task_id = {task_id}
    """

    TIMER_TIME_SUM_SELECT_SQL ="""
    SELECT
        DATE_FORMAT(commit_time,'%k:%i') as commit_time
    FROM
        commits
    WHERE
        task_id = {task_id}
        AND commit_date = '{commit_date}'
    """

    ####################
    ###### DELETE ######
    ####################
    PROJECT_DELETE_SQL = """
    DELETE FROM
        projects
    WHERE
        project_id = {project_id}
    """

    PROCESS_DELETE_SQL = """
    DELETE FROM
        processes
    WHERE
        process_id = {process_id}
    """    

    TASK_DELETE_SQL = """
    DELETE FROM
        tasks
    WHERE
        task_id = {task_id}
    """