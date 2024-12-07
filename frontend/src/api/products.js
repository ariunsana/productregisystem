import axios from 'axios';

const API_URL = 'http://localhost:8000/api';

export default {
    getProducts() {
        return axios.get(`${API_URL}/products/`);
    },
    createProduct(product) {
        return axios.post(`${API_URL}/products/`, product);
    }
}; 