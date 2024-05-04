import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

def plot_sine_wave():
    x = np.linspace(0, 2*np.pi, 100)
    y = np.sin(x)
    plt.plot(x, y)
    plt.xlabel('x')
    plt.ylabel('sin(x)')
    plt.title('Sine Wave')
    st.pyplot()

def main():
    st.title('Simple Streamlit App')
    st.write('This is a basic Streamlit app for testing deployment.')

    plot_sine_wave()

if __name__ == '__main__':
    main()
