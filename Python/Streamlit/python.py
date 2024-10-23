import streamlit as st
import numpy as np
import pandas as pd
# from streamlit_extras.let_it_rain import rain 

import time

'Starting a long computation...'

# Add a placeholder
latest_iteration = st.empty()
bar = st.progress(0)

for i in range(50):
  # Update the progress bar with each iteration.
  latest_iteration.text(f'Iteration {i+1}')
  bar.progress((i*2)+1)
  time.sleep(0.1)

'...and now we\'re done!'

#Title
st.title("Random Chart!")

chart_data = pd.DataFrame(
    np.random.rand(5,3),
    columns=['a','b','c']
)

st.line_chart(chart_data)

