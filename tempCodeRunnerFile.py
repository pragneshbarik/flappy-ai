 if self.pipes.pipes[0].up.rect.left < self.bird.rect.left :
            self.temp_score += 1
            if(self.temp_score//100  != self.score) :
                self.score = self.temp_score//100 
                print(self.score + 1)