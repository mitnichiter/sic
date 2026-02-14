import axios from 'axios';

const API_URL = 'http://localhost:8000';

export interface Cluster {
    id: number;
    name: str;
    description: string;
    frequency_score: number;
    intensity_score: number;
    engagement_score: number;
    recency_score: number;
    total_validation_score: number;
    generated_ideas: Idea[];
}

export interface Idea {
    title: string;
    description: string;
    solution_type: string;
    monetization_strategy: string;
    market_size_estimate: string;
}

export const fetchClusters = async (): Promise<Cluster[]> => {
    try {
        const response = await axios.get(`${API_URL}/clusters`);
        return response.data;
    } catch (error) {
        console.error("Error fetching clusters:", error);
        return [];
    }
};

export const fetchClusterDetails = async (id: number): Promise<Cluster | null> => {
    try {
        const response = await axios.get(`${API_URL}/clusters/${id}`);
        return response.data;
    } catch (error) {
        console.error(`Error fetching cluster ${id}:`, error);
        return null;
    }
};
