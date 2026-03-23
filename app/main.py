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
    backlog_list=[]
    with open('tasks.csv', mode='r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if datetime.fromisoformat(row['deadline']) < datetime.now():
                backlog_list.append(row['name'])
            else:
                task_list.append(row['name'])
    return render_template("index.html", task_list=task_list, backlog_list=backlog_list)

@app.route('/add', methods=['GET', 'POST'])
def new_task_form_submission():
    # Fill task_list with items from tasks.csv
    task_list=[]
    backlog_list=[]
    with open('tasks.csv', mode='r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if datetime.fromisoformat(row['deadline']) < datetime.now():
                backlog_list.append(row['name'])
            else:
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
        time_until_due = max(1, math.floor((task_deadline - datetime.now()).total_seconds() / 60))
        importance = abs(int(task_priority) / int(time_until_due))

        # Add new task as a row in tasks.csv and append new task name to task_list
        with open('tasks.csv', mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([task_name, task_deadline, task_priority, task_length, time_until_due, importance])
            if task_deadline < datetime.now():
                backlog_list.append(task_name)
            else:
                task_list.append(task_name)

        # Return and re-render HTML with updated task_list
        return redirect(url_for('new_task_form_submission'))
    return render_template('index.html', task_list=task_list, backlog_list=backlog_list)

@app.route('/remove', methods=['GET', 'POST'])
def remove_task_form_submission():
    # Fill task_list with items from tasks.csv
    rows=[]
    task_list=[]
    backlog_list=[]
    with open('tasks.csv', mode='r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        fieldnames = reader.fieldnames
        for row in reader:
            rows.append(row)
            if datetime.fromisoformat(row['deadline']) < datetime.now():
                backlog_list.append(row['name'])
            else:
                task_list.append(row['name'])

    # If form has been submitted remove task from task_list and tasks.csv
    if request.method == 'POST':
        with open('tasks.csv', mode='w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            for task in rows:
                if task['name'] == request.form.get('remove_task_name'):
                    if task['name'] in task_list:
                        task_list.remove(task['name'])
                    elif task['name'] in backlog_list:
                        backlog_list.remove(task['name'])
                else:
                    writer.writerow(task)

        # Return and re-render HTML with updated task_list
        return redirect(url_for('remove_task_form_submission'))
    return render_template('index.html', task_list=task_list, backlog_list=backlog_list)

@app.route('/tasks.json')
def get_tasks_json():
    # Get rows from tasks.csv
    rows=[]
    with open('tasks.csv', mode='r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        fieldnames = reader.fieldnames
        for row in reader:
            rows.append(row)

    # Update time_until_due and importance in tasks.csv
    # Also update tasks_info with task name, length, and importance to send back to HTML
    tasks_info = []
    with open('tasks.csv', mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for task in rows:
            time_until_due = max(1, math.floor((datetime.fromisoformat(task['deadline']) - datetime.now()).total_seconds() / 60))
            importance = abs(int(task['priority']) / int(time_until_due))
            task['time_until_due'] = time_until_due
            task['importance'] = importance
            tasks_info.append({
                "name": task['name'],
                "length": int(task['length']),
                "importance": task['importance']
            })
            writer.writerow(task)

    return jsonify(tasks_info)

@app.route('/blocks.json')
def get_blocks_json():
    # Get day and time start for a time block from blocks.csv
    # Also create blocks with name, start, length, and the time between now and the block
    blocks = []
    today = datetime.now().date()
    with open("blocks.csv", mode='r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            start_dt = datetime.fromisoformat(row['start'])
            day_diff = (start_dt.date() - today).days
            if 0 <= day_diff < 7:
                blocks.append({
                    "name": row['name'],
                    "start": row['start'],
                    "length": int(row['length']),
                    "day_index": day_diff 
                })

    return jsonify(blocks)

@app.route('/add_block', methods=['POST'])
def add_block():
    # Get block name, start, and length from form and write to blocks.csv
    name = request.form.get('blockName')
    start = request.form.get('blockStart')
    length = request.form.get('blockLength')
    with open("blocks.csv", mode='a', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['name', 'start', 'length'])
        writer.writerow({
            'name': name,
            'start': start,
            'length': length
        })

    return redirect(url_for('run_app'))