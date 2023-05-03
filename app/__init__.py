from flask import Flask, request, jsonify, render_template
import sqlite3


app = Flask(__name__, static_folder='static')

from app import views


