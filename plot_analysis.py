import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Load the data
df = pd.read_csv('Address.csv')
df2 = pd.read_csv('Transactions.csv')

# Data Cleaning
df['Is Contract?'] = df['Is Smart Contract?'].map({'Y': True, 'N': False})
df['TX Received'] = pd.to_numeric(df['TX Received'], errors='coerce')
df['TX Sent'] = pd.to_numeric(df['TX Sent'], errors='coerce')
df['Total TX'] = df['TX Received'] + df['TX Sent']


# 1. Create Enhanced Category Labels
def categorize_address(row):
    name = str(row['Name']).lower()
    is_contract = row['Is Smart Contract?']

    if 'shuffle-ftx-mevbot' in name:
        return 'ftx_mev_bot'
    elif 'ftx-hack-token' in name:
        return 'ftx_hack_token'
    elif 'shuffle.com' in name:
        return 'ftx_associated'
    elif any(x in name for x in ['coinbase', 'metamask']):
        return 'cex'
    elif any(x in name for x in ['1inch', 'cow protocol']):
        return 'defi'
    elif ('noah' in name or 'hogan' in name or
          (name not in ['', 'nan'] and not is_contract)):
        return 'individual'
    elif any(x in name for x in ['hacker', 'drainer', 'exploiter',
                                 'on chainabuse']):
        return 'exploiter'
    else:
        return 'unlabeled'


df['Category'] = df.apply(categorize_address, axis=1)

# 2. Chart 1: Transaction Volume by Category (Bar Chart)
category_tx = (df.groupby('Category')['Total TX']
               .sum()
               .sort_values(ascending=False))

fig1 = px.bar(
    x=category_tx.index,
    y=category_tx.values,
    title='Total Transaction Volume by Address Category',
    labels={'x': 'Category', 'y': 'Total Transactions (Log Scale)'},
    log_y=True,
    color=category_tx.index
)
fig1.show()

# 3. Chart 2: Smart Contract vs. EOA by Category (Stacked Bar Chart)
contract_summary = (df.groupby(['Category', 'Is Smart Contract?'])
                    .size()
                    .unstack(fill_value=0))

fig2 = px.bar(
    contract_summary,
    barmode='stack',
    title='Smart Contract vs EOA Distribution by Category',
    labels={'value': 'Number of Addresses', 'Category': 'Category'}
)
fig2.show()

# 4. Chart 3: Transaction Behavior Scatter Plot
fig3 = px.scatter(
    df,
    x='TX Received',
    y='TX Sent',
    color='Category',
    hover_data=['Address', 'Name'],
    title='Transaction Behavior: Received vs Sent',
    log_x=True,
    log_y=True
)

# Add a y=x line for reference
fig3.add_trace(
    go.Scatter(
        x=[1, 1e8],
        y=[1, 1e8],
        mode='lines',
        line=dict(dash='dash', color='grey'),
        name='y = x (Balance Line)'
    )
)
fig3.show()

# 5. Chart 4: Top 10 Addresses by Total TX Volume
top_10 = df.nlargest(10, 'Total TX')
top_10['Label'] = (top_10['Address'].str[:8] + '... (' +
                   top_10['Category'] + ')')

fig4 = px.bar(
    top_10,
    y='Label',
    x='Total TX',
    orientation='h',
    title='Top 10 Addresses by Total Transaction Volume',
    color='Category'
)
fig4.update_layout(yaxis={'categoryorder': 'total ascending'})
fig4.show()
