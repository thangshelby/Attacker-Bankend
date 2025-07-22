import express from 'express';
import client from '../grpcClient.js'; // Adjust the path as necessary

const pythonRouter = express.Router();

pythonRouter.post('/predict', async (req, res) => {
    console.log(req.body);
    const { features } = req.body;
    console.log('Received features:', features);
    
    if (!features || !Array.isArray(features)) {
        return res.status(400).json({ error: 'Invalid input data - features must be an array' });
    }

    try {
        // Structure the data according to the proto file (PredictReq message)
        const request = { features: features };
        console.log('Sending to gRPC:', request);
        
        const response = await new Promise((resolve, reject) => {
            client.Predict(request, (error, response) => {
                if (error) {
                    reject(error);
                } else {
                    resolve(response);
                }
            });
        });
        
        res.json(response);
    } catch (error) {
        console.error('Error during prediction:', error);
        res.status(500).json({ error: 'Internal server error' });
    }
});

export default pythonRouter;