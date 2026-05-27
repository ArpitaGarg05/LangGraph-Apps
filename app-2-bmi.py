from langgraph.graph import StateGraph, START, END
from typing_extensions import TypedDict

class BMIState(TypedDict):
    weight: float
    height: float
    bmi: float
    category: str # underweight / normal / overweight / obese

# Node-1: Calculate BMI
def calculate_bmi(state: BMIState) -> BMIState:
    weight = state['weight']
    height = state['height']
    state['bmi'] = weight / (height**2)
    return state

# Node-2: Classifies BMI values
def classify_bmi(state: BMIState) -> BMIState:
    bmi = state['bmi']
    if bmi < 18.5:
        state['category'] = "underweight"
    elif bmi < 25:
        state['category'] = "normal"
    elif bmi < 30:
        state['category'] = "overweight"
    else:
        state['category'] = "obese"

    return state

# Build the graph
graph = StateGraph(BMIState)

# Add nodes
graph.add_node("calculate_bmi", calculate_bmi)
graph.add_node("classify_bmi", classify_bmi)

# Add edges
graph.add_edge(START, "calculate_bmi")
graph.add_edge("calculate_bmi", "classify_bmi")
graph.add_edge("classify_bmi", END)

# Compile the graph
app = graph.compile()

# Run the application
initial_state = {"weight": 70, "height": 1.75}
result = app.invoke(initial_state) # result contains: weight, height, bmi, category
print(result)