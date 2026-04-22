import { useEffect, useMemo, useState } from 'react'
import './App.css'

const API_BASE = 'https://smart-wholesale-cart-optimizer-production.up.railway.app'

function App() {
  const [catalog, setCatalog] = useState([])
  const [quantities, setQuantities] = useState({})
  const [budgetInput, setBudgetInput] = useState('7000')
  const [budget, setBudget] = useState(7000)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')
  const [result, setResult] = useState(null)
  const [viewKnapsack, setViewKnapsack] = useState(false)

  useEffect(() => {
    const loadCatalog = async () => {
      try {
        const response = await fetch(`${API_BASE}/api/catalog`)
        if (!response.ok) {
          throw new Error('Unable to fetch catalog.')
        }
        const data = await response.json()
        setCatalog(data.items ?? [])
      } catch (loadError) {
        setError(loadError.message || 'Catalog loading failed.')
      }
    }

    loadCatalog()
  }, [])

  const selectedItems = useMemo(() => {
    return catalog
      .map((item) => ({ ...item, quantity: quantities[item.id] || 0 }))
      .filter((item) => item.quantity > 0)
  }, [catalog, quantities])

  const totalCost = useMemo(() => {
    return selectedItems.reduce((sum, item) => sum + item.price * item.quantity, 0)
  }, [selectedItems])

  const totalUnits = useMemo(() => {
    return selectedItems.reduce((sum, item) => sum + item.quantity, 0)
  }, [selectedItems])

  const budgetUsage = budget > 0 ? Math.min((totalCost / budget) * 100, 100) : 0
  const maxSlider = Math.max(25000, totalCost + 5000)
  const performance = result?.metadata ?? {}
  const visualization = result?.visualization ?? {}
  const tracebackCellMap = useMemo(() => {
    return new Map((visualization.traceback_path ?? []).map((step) => [`${step.row}-${step.col}`, step.decision]))
  }, [visualization.traceback_path])

  const updateQuantity = (itemId, delta) => {
    setQuantities((prev) => {
      const current = prev[itemId] || 0
      const next = Math.max(0, Math.min(20, current + delta))
      return { ...prev, [itemId]: next }
    })
  }

  const normalizeBudget = (rawValue) => {
    const numeric = Number(rawValue)
    if (!Number.isFinite(numeric)) {
      return 0
    }
    return Math.max(0, Math.floor(numeric))
  }

  const onBudgetInputChange = (value) => {
    setBudgetInput(value)
    const parsed = normalizeBudget(value)
    setBudget(parsed)
  }

  const runOptimization = async (nextBudget = budget) => {
    if (nextBudget <= 0) {
      setError('Budget must be at least Rs. 1')
      setResult(null)
      return
    }

    if (selectedItems.length === 0) {
      setError('Please select at least one item quantity to optimize.')
      setResult(null)
      return
    }

    setError('')
    setIsLoading(true)

    try {
      const payload = {
        budget: nextBudget,
        cart_items: selectedItems.map((item) => ({
          item_id: item.id,
          quantity: item.quantity,
        })),
        include_visualization: viewKnapsack,
      }

      const response = await fetch(`${API_BASE}/api/optimize`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      })

      const data = await response.json()
      if (!response.ok) {
        throw new Error(data.detail || 'Optimization failed')
      }

      setResult(data)
    } catch (requestError) {
      setError(requestError.message || 'Optimization request failed.')
      setResult(null)
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    if (selectedItems.length === 0 || budget <= 0) {
      return undefined
    }

    const timeoutId = setTimeout(() => {
      runOptimization(budget)
    }, 450)

    return () => clearTimeout(timeoutId)
  }, [budget, viewKnapsack, quantities])

  return (
    <div className="app-shell">
      <header className="hero">
        <p className="eyebrow">Wholesale planning with dynamic programming</p>
        <h1>Smart Wholesale Cart Optimizer</h1>
        <p className="subtitle">
          Pick quantities from the catalog, set your budget, and let 0/1 Knapsack choose
          the best combination with top alternatives.
        </p>
      </header>

      <main className="layout-grid">
        <section className="panel budget-panel">
          <h2>1. Budget Input</h2>
          <label htmlFor="budget-input">Enter Budget (Rs.)</label>
          <input
            id="budget-input"
            type="number"
            min="1"
            value={budgetInput}
            onChange={(event) => onBudgetInputChange(event.target.value)}
          />
          <div className="slider-wrap">
            <span>What-if Budget</span>
            <input
              type="range"
              min="500"
              max={maxSlider}
              step="100"
              value={Math.min(Math.max(budget, 500), maxSlider)}
              onChange={(event) => onBudgetInputChange(event.target.value)}
            />
            <p>Current budget: Rs. {budget.toLocaleString()}</p>
          </div>

          <div className="meter-block">
            <p>Budget usage: {budgetUsage.toFixed(1)}%</p>
            <div className="meter-track">
              <div className="meter-fill" style={{ width: `${budgetUsage}%` }} />
            </div>
          </div>

          <div className="button-row">
            <button
              type="button"
              className="primary"
              onClick={() => runOptimization(budget)}
              disabled={isLoading}
            >
              {isLoading ? 'Optimizing...' : 'Optimize Cart'}
            </button>
            <button
              type="button"
              className="secondary"
              onClick={() => setViewKnapsack((prev) => !prev)}
            >
              {viewKnapsack ? 'Hide Knapsack Process' : 'View Knapsack Process'}
            </button>
          </div>

          {error && <p className="error-text">{error}</p>}
        </section>

        <section className="panel catalog-panel">
          <h2>2. Item Catalog</h2>
          <div className="catalog-grid">
            {catalog.map((item) => {
              const qty = quantities[item.id] || 0
              return (
                <article
                  key={item.id}
                  className={`item-card ${qty > 0 ? 'active' : ''}`}
                >
                  <div>
                    <h3>{item.name}</h3>
                    <p>{item.category}</p>
                    <strong>Rs. {item.price.toLocaleString()}</strong>
                  </div>
                  <div className="qty-controls">
                    <button type="button" onClick={() => updateQuantity(item.id, -1)}>
                      -
                    </button>
                    <span>{qty}</span>
                    <button type="button" onClick={() => updateQuantity(item.id, 1)}>
                      +
                    </button>
                  </div>
                </article>
              )
            })}
          </div>
        </section>

        <section className="panel cart-panel">
          <h2>3. Cart Summary</h2>
          {selectedItems.length === 0 ? (
            <p className="muted">No items selected yet.</p>
          ) : (
            <div className="cart-list">
              {selectedItems.map((item) => (
                <div key={item.id} className="cart-row">
                  <span>
                    {item.name} x {item.quantity}
                  </span>
                  <span>Rs. {(item.price * item.quantity).toLocaleString()}</span>
                </div>
              ))}
            </div>
          )}

          <div className="summary-totals">
            <p>Total cart cost: Rs. {totalCost.toLocaleString()}</p>
            <p>Total selected units: {totalUnits}</p>
            {totalCost > budget && (
              <p className="warning-text">Warning: Cart total exceeds your budget.</p>
            )}
          </div>
        </section>

        <section className="panel output-panel">
          <h2>4. Optimizer Output</h2>
          {!result ? (
            <p className="muted">Run optimization to see best combinations.</p>
          ) : (
            <>
              <div className="performance-grid">
                <article className="performance-card">
                  <span>Algorithm</span>
                  <strong>{performance.algorithm || '0/1 Knapsack (Dynamic Programming)'}</strong>
                </article>
                <article className="performance-card">
                  <span>Time complexity</span>
                  <strong>{performance.time_complexity || 'O(nW)'}</strong>
                </article>
                <article className="performance-card">
                  <span>Time taken</span>
                  <strong>
                    {typeof performance.time_taken_ms === 'number'
                      ? `${performance.time_taken_ms.toFixed(2)} ms`
                      : '—'}
                  </strong>
                </article>
              </div>

              <div className="best-box">
                <h3>{result.best_option?.label || 'Best Option'}</h3>
                <p>Maximum number of items: {result.best_option?.total_items || 0}</p>
                <p>Total cost: Rs. {(result.best_option?.total_cost || 0).toLocaleString()}</p>
                <p>Budget usage: {result.best_option?.budget_usage_percent || 0}%</p>
              </div>

              <div className="options-grid">
                {(result.top_options || []).map((option, index) => (
                  <article key={`${option.label}-${index}`} className="option-card">
                    <h4>{option.label}</h4>
                    <p>Items: {option.total_items}</p>
                    <p>Cost: Rs. {option.total_cost.toLocaleString()}</p>
                    <ul>
                      {option.items.map((item) => (
                        <li key={`${option.label}-${item.item_id}`}>
                          {item.name} x {item.quantity}
                        </li>
                      ))}
                    </ul>
                  </article>
                ))}
              </div>
            </>
          )}
        </section>

        {viewKnapsack && result?.visualization && (
          <section className="panel visualize-panel">
            <h2>5. Knapsack Process Visualization</h2>
            <p>
              Price divisor used for scaled DP table: {result.visualization.price_divisor}
            </p>
            <p className="muted">
              Highlighted cells show the traceback route from the optimal state back to the start.
            </p>

            <div className="trace-legend">
              <span><i className="legend-swatch include" /> Include</span>
              <span><i className="legend-swatch exclude" /> Exclude</span>
              <span><i className="legend-swatch start" /> Start</span>
            </div>

            <div className="table-scroll">
              <table>
                <tbody>
                  {result.visualization.table_preview.map((row, rowIndex) => (
                    <tr key={`dp-row-${rowIndex}`}>
                      {row.map((cell, cellIndex) => (
                        (() => {
                          const absoluteRow = rowIndex + (result.visualization.row_offset || 0)
                          const absoluteCol = cellIndex + (result.visualization.col_offset || 0)
                          const decision = tracebackCellMap.get(`${absoluteRow}-${absoluteCol}`)
                          const cellClass = decision ? `trace-cell trace-${decision}` : 'trace-cell'

                          return (
                            <td key={`dp-cell-${rowIndex}-${cellIndex}`} className={cellClass}>
                              {cell}
                            </td>
                          )
                        })()
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {result.visualization.table_truncated && (
              <p className="muted">Table preview is truncated for readability.</p>
            )}

            <div className="steps-list">
              {result.visualization.decision_steps.map((step) => (
                <div key={`step-${step.step}-${step.item}`} className="step-card">
                  <p>
                    Step {step.step}: {step.item} - <strong>{step.decision.toUpperCase()}</strong>
                  </p>
                  <small>{step.details}</small>
                </div>
              ))}
            </div>
          </section>
        )}
      </main>
    </div>
  )
}

export default App
