from builtins import range
from datetime import timedelta

import airflow
from airflow.models import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.dummy_operator import DummyOperator
from airflow.contrib.operators.kubernetes_pod_operator import KubernetesPodOperator

args = {
    'owner': 'airflow',
    'start_date': airflow.utils.dates.days_ago(2),
}

dag = DAG(
    dag_id='pod_operator_dag',
    default_args=args,
    schedule_interval='0 0 * * *',
    dagrun_timeout=timedelta(minutes=60),
)

run_this_last = DummyOperator(
    task_id='run_this_last',
    dag=dag,
)

# [START howto_operator_bash]
run_this = BashOperator(
    task_id='run_after_loop',
    bash_command='echo 1',
    dag=dag,
)
# [END howto_operator_bash]

run_this >> run_this_last

for i in range(3):
    task = BashOperator(
        task_id='runme_' + str(i),
        bash_command='echo "{{ task_instance_key_str }}" && sleep 1',
        dag=dag,
    )
    task >> run_this

# [START howto_operator_bash_template]
also_run_this = BashOperator(
    task_id='also_run_this',
    bash_command='echo "run_id={{ run_id }} | dag_run={{ dag_run }}"',
    dag=dag,
)
# [END howto_operator_bash_template]

passing = KubernetesPodOperator(
    namespace='default',
    image='python:3',
    name='passing-test',
    in_cluster=True,
    cmds=["python","-c"],
    arguments=["print('hello world')"],
    labels={"foo": "bar"},
    task_id="passing-task",
    get_logs=True,
    dag=dag
)

also_run_this >> passing >> run_this_last

if __name__ == "__main__":
    dag.cli()
