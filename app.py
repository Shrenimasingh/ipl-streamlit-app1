import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
from collections import defaultdict, deque

st.set_page_config(page_title="IPL Match Analyzer", layout="wide")

st.title("🏏 IPL Match Analyzer")

# -------- Helper Functions --------
def parse_match_data(raw_text):
    lines = raw_text.strip().split('\n')
    if len(lines) != 20:
        return None, "❌ Please enter exactly 20 match records."

    graph = defaultdict(set)
    teams = set()

    try:
        for line in lines:
            parts = line.split()
            if len(parts) != 4:
                return None, "❌ Each line must be: TeamA ScoreA TeamB ScoreB"
            t1, s1, t2, s2 = parts
            s1, s2 = int(s1), int(s2)
            if s1 > s2:
                graph[t1].add(t2)
            else:
                graph[t2].add(t1)
            teams.update([t1, t2])
    except:
        return None, "❌ Invalid format or score. Make sure scores are integers."

    return graph, sorted(teams)

def can_reach(start, end, graph):
    visited = set()
    queue = deque([start])
    while queue:
        curr = queue.popleft()
        if curr == end:
            return True
        for neighbor in graph[curr]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
    return False

def analyze_result(graph, teamA, teamB):
    a_beats_b = teamB in graph[teamA]
    b_beats_a = teamA in graph[teamB]
    a_indirect_b = can_reach(teamA, teamB, graph)
    b_indirect_a = can_reach(teamB, teamA, graph)

    if a_beats_b:
        return f"✅ {teamA} DEFEATED {teamB} (Direct)"
    elif b_beats_a:
        return f"✅ {teamB} DEFEATED {teamA} (Direct)"
    elif a_indirect_b and not b_indirect_a:
        return f"🟠 {teamA} DEFEATED {teamB} INDIRECTLY"
    elif b_indirect_a and not a_indirect_b:
        return f"🟠 {teamB} DEFEATED {teamA} INDIRECTLY"
    elif a_indirect_b and b_indirect_a:
        return f"🔄 {teamA} AND {teamB} HAVE DEFEATED EACH OTHER INDIRECTLY"
    else:
        return f"⚪ {teamA} AND {teamB} ARE NOT COMPARABLE"

def draw_graph(graph):
    G = nx.DiGraph()
    for winner in graph:
        for loser in graph[winner]:
            G.add_edge(winner, loser)

    pos = nx.spring_layout(G, seed=42)
    plt.figure(figsize=(10, 6))
    nx.draw(G, pos, with_labels=True, arrows=True,
            node_color="skyblue", edge_color="gray",
            node_size=2000, font_size=10, font_weight='bold', arrowsize=20)
    st.pyplot(plt.gcf())  # Use current figure

# -------- Streamlit UI --------
with st.expander("📋 Enter 20 Match Records (Format: TeamA ScoreA TeamB ScoreB)"):
    default_text = "\n".join([
        "MI 17 CSK 14", "RCB 27 SRH 10", "KKR 24 RR 10", "CSK 24 PBKS 19",
        "MI 35 RCB 26", "PBKS 17 SRH 10", "RCB 27 KKR 10", "MI 24 PBKS 10",
        "SRH 21 DC 14", "KKR 31 RR 13", "MI 10 DC 7", "DC 17 CSK 14",
        "RCB 34 RR 13", "CSK 30 RR 7", "MI 31 SRH 14", "PBKS 42 DC 17",
        "RCB 17 CSK 14", "RR 31 SRH 14", "RCB 21 PBKS 17", "CSK 31 SRH 27"
    ])
    match_data = st.text_area("Paste or type 20 matches below:", value=default_text, height=300)

if st.button("✅ Load Matches"):
    match_graph, msg = parse_match_data(match_data)
    if match_graph:
        st.session_state['graph'] = match_graph
        st.session_state['teams'] = msg
        st.success("✔ Match data loaded successfully!")
    else:
        st.error(msg)

if 'graph' in st.session_state:
    col1, col2 = st.columns(2)
    with col1:
        teamA = st.selectbox("Select Team A", st.session_state['teams'], key="teamA")
    with col2:
        teamB = st.selectbox("Select Team B", st.session_state['teams'], key="teamB")

    if st.button("🔍 Analyze Result"):
        result = analyze_result(st.session_state['graph'], teamA, teamB)
        st.markdown(f"### {result}")

    if st.button("📈 Show Win/Loss Graph"):
        draw_graph(st.session_state['graph'])
