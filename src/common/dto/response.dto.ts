
export interface MatchResponse {
    statusCode: number;
    message: string; 
    data?: {
      
    }
}

export class ResponseDto implements MatchResponse {
    constructor(
        public statusCode: number,
        public message: string, 
        public data?: { 
        }
    ) { }
}