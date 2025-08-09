import React, { useState, useEffect } from "react";
import axios from "axios";
import "./App.css";
const BASE_URL = "https://your-backend-service-name.onrender.com/api";
function App() {
  const [products, setProducts] = useState([]);
  const [form, setForm] = useState({ name: "", sku: "", description: "" });
  const [inventory, setInventory] = useState([]);
  const [stockForm, setStockForm] = useState({
    transaction_type: "IN",
    product: "",
    quantity: "",
  });
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [transactionHistory, setTransactionHistory] = useState([]);
  const [showHistory, setShowHistory] = useState(false);
  

  useEffect(() => {
    fetchProducts();
    fetchInventory();
  }, []);

  const fetchProducts = async () => {
    try {
      const response = await axios.get("https://warehouse-tracker-web-app.onrender.com/api/products/");
      setProducts(response.data);
    } catch (err) {
      console.error("Error fetching products:", err);
    }
  };

  const fetchInventory = async () => {
    try {
      const response = await axios.get("https://warehouse-tracker-web-app.onrender.com/api/inventory-summary/");
      setInventory(response.data);
    } catch (err) {
      console.error("Error fetching inventory:", err);
    }
  };

  const fetchTransactionHistory = async (productName) => {
    try {
      
      const response = await axios.get(`https://warehouse-tracker-web-app.onrender.com/api/transactions/history/${encodeURIComponent(productName)}/`);
      setTransactionHistory(response.data);
      setSelectedProduct(productName);
      setShowHistory(true);
    } catch (err) {
      console.error("Error fetching transaction history:", err);
      
      try {
        const allTransactions = await axios.get("https://warehouse-tracker-web-app.onrender.com/api/transactions/");
        const filteredTransactions = allTransactions.data.filter(transaction => 
          transaction.details.some(detail => {
            const product = products.find(p => p.id === detail.product);
            return product && product.name === productName;
          })
        ).map(transaction => ({
          ...transaction,
          details: transaction.details.filter(detail => {
            const product = products.find(p => p.id === detail.product);
            return product && product.name === productName;
          })
        }));
        setTransactionHistory(filteredTransactions);
        setSelectedProduct(productName);
        setShowHistory(true);
      } catch (fallbackErr) {
        console.error("Error fetching all transactions:", fallbackErr);
        alert("Unable to fetch transaction history");
      }
    }
  };

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleAdd = async () => {
    try {
      const res = await axios.post("https://warehouse-tracker-web-app.onrender.com/api/products/", form);
      setProducts([...products, res.data]);
      setForm({ name: "", sku: "", description: "" });
      
      fetchInventory();
    } catch (err) {
      console.error("Error adding product:", err);
    }
  };

  const handleStockChange = (e) => {
    setStockForm({ ...stockForm, [e.target.name]: e.target.value });
  };

  const handleStockSubmit = async () => {
    try {
      console.log("Submitting:", stockForm);

      
      if (stockForm.transaction_type === "OUT") {
        const selectedProduct = inventory.find(item => item.product === products.find(p => p.id == stockForm.product)?.name);
        const currentStock = selectedProduct ? selectedProduct.current_stock : 0;
        const requestedQuantity = parseInt(stockForm.quantity);

        if (requestedQuantity > currentStock) {
          alert(`Cannot remove ${requestedQuantity} items. Only ${currentStock} items available in stock.`);
          return;
        }
      }

      const payload = {
        transaction_type: stockForm.transaction_type,
        details: [
          {
            product: stockForm.product,
            quantity: parseInt(stockForm.quantity),
          },
        ],
      };

      const transaction = await axios.post(
        "https://warehouse-tracker-web-app.onrender.com/api/transactions/",
        payload
      );

      console.log("Transaction successful:", transaction.data);

      
      await fetchInventory();

      
      setStockForm({
        transaction_type: "IN",
        product: "",
        quantity: "",
      });

      console.log("Inventory updated successfully");
    } catch (error) {
      console.error("Error handling stock transaction: ", error.response?.data || error.message);
    }
  };

  const formatDateTime = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    });
  };

  const closeHistory = () => {
    setShowHistory(false);
    setSelectedProduct(null);
    setTransactionHistory([]);
  };

  return (
    <div className="container">
      <h1>Warehouse Tracker</h1>

      {/* Product List */}
      <div className="card">
        <h2>Product List</h2>
        {products.length === 0 ? (
          <p>No products found.</p>
        ) : (
          <ul>
            {products.map((p) => (
              <li key={p.id} className="product-item">
                <div className="product-name"><strong>{p.name}</strong></div>
                <div className="product-sku">SKU: {p.sku}</div>
                <div className="product-description">{p.description}</div>
              </li>
            ))}
          </ul>
        )}
      </div>

      {/* Add Product */}
      <div className="card">
        <h2>Add Product</h2>
        <input type="text" name="name" placeholder="Product Name" value={form.name} onChange={handleChange} />
        <input type="text" name="sku" placeholder="SKU" value={form.sku} onChange={handleChange} />
        <input type="text" name="description" placeholder="Description" value={form.description} onChange={handleChange} />
        <button onClick={handleAdd}>Add</button>
      </div>

      {/* Add Stock Transaction */}
      <div className="card">
        <h2>Add Stock Transaction</h2>
        <select name="transaction_type" value={stockForm.transaction_type} onChange={handleStockChange}>
          <option value="IN">IN</option>
          <option value="OUT">OUT</option>
        </select>
        <select name="product" value={stockForm.product} onChange={handleStockChange}>
          <option value="">Select Product</option>
          {products.map((p) => {
            const inventoryItem = inventory.find(item => item.product === p.name);
            const currentStock = inventoryItem ? inventoryItem.current_stock : 0;
            return (
              <option key={p.id} value={p.id}>
                {p.name} (Stock: {currentStock})
              </option>
            );
          })}
        </select>
        <input
          type="number"
          name="quantity"
          placeholder="Quantity"
          value={stockForm.quantity}
          onChange={handleStockChange}
          min="1"
        />
        <button onClick={handleStockSubmit}>Submit</button>
        
        {/* Show current stock info when OUT is selected */}
        {stockForm.transaction_type === "OUT" && stockForm.product && (
          <div style={{marginTop: "10px", color: "#666"}}>
            Current stock: {
              inventory.find(item => 
                item.product === products.find(p => p.id == stockForm.product)?.name
              )?.current_stock || 0
            } items available
          </div>
        )}
      </div>

      {/* Inventory Summary */}
      <div className="card">
        <h2>Inventory Summary</h2>
        {inventory.length === 0 ? (
          <p>No inventory data.</p>
        ) : (
          <ul>
            {inventory.map((item, index) => (
              <li 
                key={index} 
                className="product-item clickable-item"
                onClick={() => fetchTransactionHistory(item.product)}
                style={{ cursor: 'pointer', border: '1px solid #ddd', margin: '5px 0', padding: '10px', borderRadius: '5px' }}
                onMouseEnter={(e) => e.target.style.backgroundColor = '#f0f0f0'}
                onMouseLeave={(e) => e.target.style.backgroundColor = 'white'}
              >
                <div><strong>{item.product}</strong></div>
                <div>SKU: {item.sku}</div>
                <div>Quantity: {item.current_stock}</div>
                <div style={{ fontSize: '12px', color: '#888', marginTop: '5px' }}>
                  Click to view transaction history
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>

      {/* Transaction History Modal */}
      {showHistory && (
        <div 
          className="modal-overlay" 
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            width: '100%',
            height: '100%',
            backgroundColor: 'rgba(0,0,0,0.5)',
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            zIndex: 1000
          }}
          onClick={closeHistory} 
        >
          <div 
            className="modal-content" 
            style={{
              backgroundColor: 'white',
              padding: '20px',
              borderRadius: '10px',
              maxWidth: '600px',
              maxHeight: '80%',
              overflow: 'auto',
              position: 'relative'
            }}
            onClick={(e) => e.stopPropagation()} 
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '15px' }}>
              <h3 style={{ margin: 0 }}>{selectedProduct} </h3>
              <button 
                onClick={closeHistory}
                style={{
                    background: '#f44336',
                    color: 'white',              
                    border: 'none',              
                    borderRadius: '3px',         
                    width: '24px',               
                    height: '24px',
                    fontSize: '16px',           
                    cursor: 'pointer',           
                    display: 'flex',             
                    alignItems: 'center',
                    justifyContent: 'center'
                  }}

                onMouseEnter={(e) => e.target.style.backgroundColor = '#d32f2f'}
                onMouseLeave={(e) => e.target.style.backgroundColor = '#f44336'}
              >
                ×
              </button>
            </div>

            
            {transactionHistory.length === 0 ? (
              <p>No transaction history found for this product.</p>
            ) : (
              <div>
                {transactionHistory.map((transaction, index) => (
                  <div key={index} style={{
                    border: '1px solid #ddd',
                    margin: '10px 0',
                    padding: '15px',
                    borderRadius: '5px',
                    backgroundColor: transaction.transaction_type === 'IN' ? '#e8f5e8' : '#ffe8e8'
                  }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
                      <span style={{
                        fontWeight: 'bold',
                        color: transaction.transaction_type === 'IN' ? '#2e7d32' : '#d32f2f'
                      }}>
                        {transaction.transaction_type === 'IN' ? 'STOCK IN' : 'STOCK OUT'}
                      </span>
                      <span style={{ fontSize: '14px', color: '#666' }}>
                        {formatDateTime(transaction.timestamp || transaction.date || new Date().toISOString())}
                      </span>
                    </div>
                    
                    {transaction.details.map((detail, detailIndex) => (
                      <div key={detailIndex}>
                        <div><strong>Quantity:</strong> {detail.quantity}</div>
                        {transaction.notes && <div><strong>Notes:</strong> {transaction.notes}</div>}
                      </div>
                    ))}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
