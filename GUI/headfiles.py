#!/usr/bin/env python
# coding: utf-8

import MySQLdb
import time
import datetime
import re
from tqdm import tqdm
import warnings
warnings.filterwarnings('ignore')

from tkinter import *
from tkinter.messagebox import *
from tkinter.ttk import Treeview

import pylab
import numpy as np
import pandas as pd
import baostock as bs

import matplotlib.pyplot as plt
from matplotlib import dates as mdates
from matplotlib import ticker as mticker
from mplfinance.original_flavor import candlestick_ohlc
from matplotlib.dates import DateFormatter, WeekdayLocator, DayLocator, MONDAY, YEARLY
from matplotlib.dates import MonthLocator,MONTHLY
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure