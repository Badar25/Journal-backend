export class CreateJournalDto {
  title: string;
  content: string;
  userId?: string; // Made optional since it comes from token
  tags?: string[];
  createdAt?: Date;
}

export class UpdateJournalDto {
  title?: string;
  content?: string; 
}