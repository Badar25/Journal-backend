import { Injectable, OnModuleInit, Logger } from '@nestjs/common';
import { QdrantClient } from '@qdrant/js-client-rest';

@Injectable()
export class QdrantService implements OnModuleInit {
  private client: QdrantClient;
  private readonly logger = new Logger(QdrantService.name);

  constructor() {
    this.client = new QdrantClient({
      url: process.env.QDRANT_URL || 'http://localhost:6333',
      timeout: 5000, // 5 seconds timeout
      checkCompatibility: false // Disable compatibility check for now
    });
  }

  async onModuleInit() {
    try {
      await this.client.getCollections();
      this.logger.log('Successfully connected to Qdrant server');
    } catch (error) {
      this.logger.error('Failed to connect to Qdrant server. Make sure Qdrant is running.');
      this.logger.error(`Error: ${error.message}`);
    }
  }

  async createCollection(collectionName: string) {
    try {
      await this.client.createCollection(collectionName, {
        vectors: {
          size: 384,
          distance: 'Cosine',
        },
      });
      return { success: true, message: `Collection ${collectionName} created successfully` };
    } catch (error) {
      throw error;
    }
  }

  async getCollections() {
    try {
      const collections = await this.client.getCollections();
      return collections;
    } catch (error) {
      throw error;
    }
  }

  async upsertPoint(collectionName: string, point: any) {
    try {
      await this.client.upsert(collectionName, {
        points: [
          {
            id: point.id,
            vector: point.vector,
            payload: point.payload
          }
        ]
      });
      return true;
    } catch (error) {
      this.logger.error(`Failed to upsert point: ${error.message}`);
      throw error;
    }
  }

  async deletePoint(collectionName: string, pointId: string) {
    try {
      await this.client.delete(collectionName, {
        points: [pointId]
      });
      return true;
    } catch (error) {
      this.logger.error(`Failed to delete point: ${error.message}`);
      throw error;
    }
  }

  async getPoint(collectionName: string, pointId: string) {
    try {
      const response = await this.client.retrieve(collectionName, {
        ids: [pointId]
      });
      return response[0];
    } catch (error) {
      this.logger.error(`Failed to get point: ${error.message}`);
      throw error;
    }
  }

  async searchPoints(collectionName: string, filter: any, limit: number = 10) {
    try {
      const response = await this.client.scroll(collectionName, {
        filter: filter,
        limit: limit,
        with_payload: true,
        with_vector: false
      });
      return response.points;
    } catch (error) {
      this.logger.error(`Failed to search points: ${error.message}`);
      throw error;
    }
  }
}