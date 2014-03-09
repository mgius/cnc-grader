#! /usr/bin/envy ruby
# baby's first ruby program

STDIN.read.split("\n").each do |a| 
   total = 0
   (0..a.to_i).each do |b|
      b.to_s.each_char do |c|
         if c == '1'
            total += 1
         end
      end
   end
   puts total
end
