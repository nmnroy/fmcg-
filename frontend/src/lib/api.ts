import axios from 'axios';

const API_URL = 'http://localhost:8000/api';

export const uploadRFP = async (file: File) => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await axios.post(`${API_URL}/process`, formData, {
        headers: {
            'Content-Type': 'multipart/form-data',
        },
    });
    return response.data;
};

export const sendChatMessage = async (message: string, context: string) => {
    const response = await axios.post(`${API_URL}/chat`, {
        message,
        context
    });
    return response.data.response;
};
