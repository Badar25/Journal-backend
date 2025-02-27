import { Module } from '@nestjs/common';
import { ConfigModule, ConfigService } from '@nestjs/config';
import { FirebaseAdminModule } from '@alpha018/nestjs-firebase-auth';
import { ExtractJwt } from 'passport-jwt';
import { JournalModule } from './journal/journal.module';
import { QdrantModule } from './qdrant/qdrant.module';

@Module({
  imports: [
    ConfigModule.forRoot(),
    FirebaseAdminModule.forRootAsync({
      imports: [ConfigModule],
      useFactory: (configService: ConfigService) => ({
        base64: configService.get('FIREBASE_SERVICE_ACCOUNT_BASE64'),
        auth: {
          config: {
            extractor: ExtractJwt.fromAuthHeaderAsBearerToken(),
            checkRevoked: true,
          },
        },
      }),
      inject: [ConfigService],
    }),
    JournalModule,
    QdrantModule,
  ],
})
export class AppModule {}