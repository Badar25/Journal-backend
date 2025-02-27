import { Module } from '@nestjs/common';
import { QdrantService } from './qdrant.service';

@Module({
  providers: [QdrantService],
  exports: [QdrantService], // Export QdrantService so other modules can use it
})
export class QdrantModule {}