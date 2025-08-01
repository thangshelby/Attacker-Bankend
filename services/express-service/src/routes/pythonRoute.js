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

// New endpoint to receive loan decision results from Python MAS
pythonRouter.post('/loan-decision', async (req, res) => {
    console.log('📥 Received loan decision from Python MAS');
    
    try {
        const { request_data, mas_result, timestamp } = req.body;
        
        console.log('Request Data:', {
            age: request_data?.age,
            loan_amount: request_data?.loan_amount_requested,
            decision: mas_result?.final_result?.decision
        });
        
        // TODO: Save to database here
        // const loanRecord = await saveLoanDecisionToDatabase({
        //     request_data,
        //     mas_result, 
        //     timestamp,
        //     created_at: new Date()
        // });
        
        // For now, just return success
        res.json({
            success: true,
            message: 'Loan decision received successfully',
            // saved_id: loanRecord?.id
        });
        
    } catch (error) {
        console.error('❌ Error saving loan decision:', error);
        res.status(500).json({ 
            success: false,
            error: 'Failed to save loan decision' 
        });
    }
});

export default pythonRouter;