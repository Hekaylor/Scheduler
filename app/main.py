# py -m flask --app main run                  # run locally
# py -m flask --app main run --host=0.0.0.0   # run globally

from flask import Flask, render_template, request, redirect, url_for, jsonify
import csv
from datetime import datetime
import math

app = Flask(__name__)

@app.route('/')
def run_app():
    task_list=[]
    with open('tasks.csv', mode='r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            task_list.append(row['name'])
    return render_template("index.html", task_list=task_list)

@app.route('/add', methods=['GET', 'POST'])
def new_task_form_submission():
    # Fill task_list with items from tasks.csv
    task_list=[]
    with open('tasks.csv', mode='r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            task_list.append(row['name'])

    # If form has been submitted add new task to task_list and tasks.csv
    priority_levels = ["low", "lowest", "medium", "high", "highest"]
    if request.method == 'POST':
        task_name = request.form.get('new_task_name')
        task_deadline = datetime.fromisoformat(request.form.get('new_task_deadline'))
        task_priority = request.form.get('new_task_priority')
        for level in priority_levels:
            if task_priority == level:
                task_priority = priority_levels.index(level) + 1
        task_length = request.form.get('new_task_length')
        time_until_due = abs(math.floor((task_deadline - datetime.now()).total_seconds() / 60))
        importance = int(task_priority) / int(time_until_due)

        # Add new task as a row in tasks.csv and append new task name to task_list
        with open('tasks.csv', mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([task_name, task_deadline, task_priority, task_length, time_until_due, importance])
            task_list.append(task_name)

        # Return and re-render HTML with updated task_list
        return redirect(url_for('new_task_form_submission'))
    return render_template('index.html', task_list=task_list)

@app.route('/remove', methods=['GET', 'POST'])
def remove_task_form_submission():
    # Fill task_list with items from tasks.csv
    rows = []
    task_list = []
    with open('tasks.csv', mode='r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        fieldnames = reader.fieldnames
        for row in reader:
            rows.append(row)
            task_list.append(row['name'])

    # If form has been submitted remove task from task_list and tasks.csv
    if request.method == 'POST':
        with open('tasks.csv', mode='w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            for task in rows:
                if task['name'] == request.form.get('remove_task_name'):
                    task_list.remove(task['name'])
                else:
                    writer.writerow(task)

        # Return and re-render HTML with updated task_list
        return redirect(url_for('remove_task_form_submission'))
    return render_template('index.html', task_list=task_list)

@app.route('/tasks.json')
def get_tasks_json():
    tasks_info = []
    with open('tasks.csv', mode='r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            tasks_info.append({
                "name": row['name'],
                "length": int(row['length']),
                "importance": row['importance']
            })

    return jsonify(tasks_info)