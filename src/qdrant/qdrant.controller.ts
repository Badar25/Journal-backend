import { Controller, Post, Get, Body, Param } from '@nestjs/common';
import { QdrantService } from './qdrant.service';

@Controller('qdrant')
export class QdrantController {
  constructor(private readonly qdrantService: QdrantService) {}

  @Post('collections/:name')
  async createCollection(@Param('name') name: string) {
    return await this.qdrantService.createCollection(name);
  }

  @Get('collections')
  async getCollections() {
    return await this.qdrantService.getCollections();
  }
}