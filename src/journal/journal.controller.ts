import { Controller, Get, Post, Put, Delete, Body, Param, UseGuards, Logger } from '@nestjs/common';
import { FirebaseGuard, FirebaseUser } from '@alpha018/nestjs-firebase-auth';
import { JournalService } from './journal.service';
import { CreateJournalDto, UpdateJournalDto } from './dto/journal.dto';

interface FirebaseData {
  user: {
    user_id: string;
    email: string;
  };
}

@Controller('journals')
@UseGuards(FirebaseGuard)
export class JournalController {
  private readonly logger = new Logger(JournalController.name);
  
  constructor(private readonly journalService: JournalService) {}

  @Post()
  async createJournal(
    @Body() dto: CreateJournalDto,
    @FirebaseUser() firebaseData: FirebaseData
  ) {
    const user = firebaseData.user;
    this.logger.debug(`Creating journal for user: ${user.user_id}`);
    
    if (!user || !user.user_id) {
      this.logger.error('No valid Firebase user found in request');
      throw new Error('Unauthorized: No valid user found');
    }

    return this.journalService.createJournal({
      ...dto,
      userId: user.user_id
    });
  }

  @Put(':id')
  async updateJournal(
    @Param('id') id: string,
    @Body() dto: UpdateJournalDto,
    @FirebaseUser() firebaseData: FirebaseData
  ) {
    const user = firebaseData.user;
    this.logger.debug(`Updating journal ${id} for user: ${user.user_id}`);
    
    return this.journalService.updateJournal(id, dto);
  }

  @Delete(':id')
  async deleteJournal(
    @Param('id') id: string,
    @FirebaseUser() firebaseData: FirebaseData
  ) {
    const user = firebaseData.user;
    this.logger.debug(`Deleting journal ${id} for user: ${user.user_id}`);
    
    return this.journalService.deleteJournal(id);
  }

  @Get()
  async getUserJournals(
    @FirebaseUser() firebaseData: FirebaseData
  ) {
    const user = firebaseData.user;
    this.logger.debug(`Fetching all journals for user: ${user.user_id}`);
    
    return this.journalService.getJournalsByUserId(user.user_id);
  }

  @Get(':id')
  async getJournal(
    @Param('id') id: string,
    @FirebaseUser() firebaseData: FirebaseData
  ) {
    const user = firebaseData.user;
    this.logger.debug(`Fetching journal ${id} for user: ${user.user_id}`);
    
    return this.journalService.getJournal(id);
  } 
}