import React, { useEffect, useState } from 'react';
import axios from 'axios';

const ProductList = () => {
  const [name, setName] = useState('');
  const [sku, setSku] = useState('');
  const [description, setDescription] = useState('');
  const [products, setProducts] = useState([]);

  const apiBaseUrl = process.env.REACT_APP_API_URL || 'http://127.0.0.1:8000/api';

  
  useEffect(() => {
    axios.get(`${apiBaseUrl}/products/`)
      .then(response => setProducts(response.data))
      .catch(error => console.error('Error fetching products:', error));
  }, [apiBaseUrl]);

  
  const handleAddProduct = () => {
    if (!name || !sku || !description) return;

    axios.post(`${apiBaseUrl}/products/`, {
      name: name,
      sku: sku,
      description: description,
    })
      .then(response => {
        setProducts([...products, response.data]);
        setName('');
        setSku('');
        setDescription('');
      })
      .catch(error => console.error('Error adding product:', error));
  };

  return (
    <div>
      <h2>Product List</h2>

      <ul>
        {products.map(product => (
          <li key={product.id}>
            {product.name} - {product.sku} - {product.description}
          </li>
        ))}
      </ul>

      <h3>Add Product</h3>
      <input
        type="text"
        placeholder="Product Name"
        value={name}
        onChange={e => setName(e.target.value)}
      />
      <input
        type="text"
        placeholder="SKU"
        value={sku}
        onChange={e => setSku(e.target.value)}
      />
      <input
        type="text"
        placeholder="Description"
        value={description}
        onChange={e => setDescription(e.target.value)}
      />
      <button onClick={handleAddProduct}>Add</button>
    </div>
  );
};

export default ProductList;
