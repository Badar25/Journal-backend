import { Injectable, Logger } from '@nestjs/common';
import { v4 as uuidv4 } from 'uuid';
import { QdrantService } from '../qdrant/qdrant.service';
import { CreateJournalDto, UpdateJournalDto } from './dto/journal.dto';

@Injectable()
export class JournalService {
  private readonly logger = new Logger(JournalService.name);
  private readonly collectionName = 'journals';

  constructor(private readonly qdrantService: QdrantService) {}

  async createJournal(dto: CreateJournalDto) {
    try {
      const point = {
        id: uuidv4(),  
        vector: new Array(384).fill(0),
        payload: {
          title: dto.title,
          content: dto.content,
          userId: dto.userId,
          createdAt: dto.createdAt || new Date(),
        },
      };

      await this.qdrantService.upsertPoint(this.collectionName, point);
      return { id: point.id, ...point.payload };
    } catch (error) {
      this.logger.error(`Failed to create journal: ${error.message}`);
      throw error;
    }
  }

  async updateJournal(id: string, dto: UpdateJournalDto) {
    try {
      // First get the existing journal to preserve userId
      const existingJournal = await this.qdrantService.getPoint(this.collectionName, id);
      
      const point = {
        id,
        vector: new Array(384).fill(0),
        payload: {
          ...existingJournal?.payload, // Preserve existing data
          ...dto,
          updatedAt: new Date(), // Optional: track update time
        },
      };

      await this.qdrantService.upsertPoint(this.collectionName, point);
      return { id, ...point.payload };
    } catch (error) {
      this.logger.error(`Failed to update journal: ${error.message}`);
      throw error;
    }
  }

  async deleteJournal(id: string) {
    try {
      await this.qdrantService.deletePoint(this.collectionName, id);
      return { success: true, message: 'Journal deleted successfully' };
    } catch (error) {
      this.logger.error(`Failed to delete journal: ${error.message}`);
      throw error;
    }
  }

  async getJournal(id: string) {
    try {
      const point = await this.qdrantService.getPoint(this.collectionName, id);
      return point ? { id, ...point.payload } : null;
    } catch (error) {
      this.logger.error(`Failed to get journal: ${error.message}`);
      throw error;
    }
  }

  async getJournalsByUserId(userId: string) {
    try {
      const filter = {
        must: [
          {
            key: 'userId',
            match: { value: userId }
          }
        ]
      };

      const points = await this.qdrantService.searchPoints(this.collectionName, filter);
      return points.map(point => ({
        id: point.id,
        ...point.payload
      }));
    } catch (error) {
      this.logger.error(`Failed to get journals by user: ${error.message}`);
      throw error;
    }
  }
}
