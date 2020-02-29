from flask import Flask, render_template
from flask_socketio import SocketIO, emit, send, join_room, leave_room, rooms
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins='*', async_handlers=True)

article_data = []
n_questions = 1
for n_question in range(1, n_questions + 1):
  with open('./data/q{}_train.json'.format(n_question)) as train_file:
    json_data = json.load(train_file)
    for j in json_data:
      if j['answer'] == 1:
        j.update(category='Question {}'.format(n_question))
        if ('annotations' not in j):
          j.update(annotations=[])
        article_data.append(j)

def get_room_name(category, article_id):
  return str(category) + ' ' + str(article_id)

def write_back():
  for n_question in range(1, n_questions + 1):
    d = [article for article in article_data if article['category'] == 'Question {}'.format(n_question)]
    with open('./data/q{}_train.json'.format(n_question), 'w') as f:
      f.write(json.dumps(d))

@app.route('/ping')
def ping():
  socketio.emit('ping event')

@socketio.on('connect')
def connect():
  pass

@socketio.on('refresh article list')
def on_refresh_article_list(data):
  category = data['category']
  return [article['id'] for article in article_data if 'id' in article and article['category'] == category]

@socketio.on('get article')
def on_get_article(data):
  category = data['category']
  article_id = data['articleId']
  for item in article_data:
    if item['id'] == article_id and item['category'] == category:
      return item
  return False

@socketio.on('join article')
def on_join_article(data):
  category = data['category']
  article_id = data['articleId']

  join_room(get_room_name(category, article_id))

@socketio.on('leave article')
def on_leave_article(data):
  category = data['category']
  article_id = data['articleId']
  leave_room(get_room_name(category, article_id))

@socketio.on('add annotation')
def on_add_annotation(data):
  category = data['category']
  article_id = data['articleId']
  annotator = data['annotator']
  sentence_index = data['sentenceIndex']
  ann = {
    'articleId': article_id,
    'sentenceIndex': sentence_index,
    'annotator': annotator,
    'category': category
  }

  for i in range(0, len(article_data)):
    if article_data[i]['id'] == article_id:
      if (len(article_data[i]['sentences']) < sentence_index):
        return
      for annotation in article_data[i]['annotations']:
        if annotation['sentenceIndex'] == sentence_index and annotation['annotator'] == annotator:
          return
      article_data[i]['annotations'].append(ann)
      room = join_room(get_room_name(category, article_id))
      emit('add annotation', ann, room=room, broadcast=True)
      write_back()
      return

@socketio.on('remove annotation')
def on_remove_annotation(data):
  category = data['category']
  article_id = data['articleId']
  annotator = data['annotator']
  sentence_index = data['sentenceIndex']

  ann = {
    'articleId': article_id,
    'sentenceIndex': sentence_index,
    'annotator': annotator,
    'category': category
  }

  for i in range(0, len(article_data)):
    if article_data[i]['id'] == article_id:
      if (len(article_data[i]['sentences']) < sentence_index):
        return
      for annotation in article_data[i]['annotations']:
        if annotation['sentenceIndex'] == sentence_index and annotation['annotator'] == annotator:
          article_data[i]['annotations'].remove(annotation)
          room = join_room(get_room_name(category, article_id))
          emit('remove annotation', ann, room=room, broadcast=True)
          write_back()
          return

if __name__ == '__main__':
  socketio.run(app)
