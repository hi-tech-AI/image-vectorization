from PIL import Image
import numpy as np
import cv2 as cv
import matplotlib.pyplot as plt, matplotlib.colors as mplc
import time


from classes.ga.ga import GA
from classes.pso.pso import PSO

# Set windows properties
cv.namedWindow('Result')

# Load image
IMAGE = 'mona_lisa'
ALGORITHM = PSO  # GA or PSO
img = cv.cvtColor(np.array(Image.open(f'samples/{IMAGE}.jpg')), cv.COLOR_RGB2BGR)

# Save result as video
fourcc = cv.VideoWriter_fourcc(*'mp4v')
out = cv.VideoWriter(f'results/{ALGORITHM.__name__}_{IMAGE}.mp4', fourcc, 30, img.shape[:2][::-1])

# Genetic algorithm
ea = GA(
    img,
    pop_size=50,
    n_poly=50,
    n_vertex=3,
    selection_cutoff=.1,
    mutation_chances=(0.01, 0.01, 0.01),
    mutation_factors=(0.2, 0.2, 0.2)
)

# Particle swarm optimization
pso = PSO(
    img,
    swarm_size=200,
    neighborhood_size=3,
    coeffs=(0.5, 0.1, 0.4), # Inertia (0.7 - 0.8), cognitive coeff, social coeff (1.5 - 1.7) # Check https://doi.org/10.1145/1830483.1830492
    min_distance=5
)

hbest = []
while True:
    start_time = time.time()

    # Compute next generation
    if ALGORITHM == GA: 
        gen, best, population = ea.next()
        fitness = best.fitness
    else: 
        gen, fitness = pso.next()

    # Print and save result
    tot_time = round((time.time() - start_time)*1000)
    print(f'{gen:04d}) {tot_time:03d}ms, fitness: {fitness}')
    hbest.append(fitness)

    # Obtain current best solution
    if ALGORITHM == GA: 
        best_img = best.draw()
    else:
        target_img = np.log(pso.problem.target+1)
        target_img = cv.normalize(target_img, None, 0, 255, norm_type=cv.NORM_MINMAX)
        target_img = cv.cvtColor(target_img.astype(np.uint8), cv.COLOR_GRAY2BGR)
        best_img = pso.draw()
        target_img = np.where(best_img[:,:] == [255,255,255], [0,0,255], target_img[:,:]).astype(np.uint8)
    
    # Show current best
    best_img = cv.resize(best_img, img.shape[1::-1])
    result = cv.resize(np.hstack([img, best_img]), None, fx=.6, fy=.6) # target_img
    cv.imshow('Result', result) 
    
    # Save result in video
    if gen % 5 == 0:
        out_frame = cv.putText(best_img.copy(), f'{gen}', (2,16), cv.FONT_HERSHEY_PLAIN, 1.3, (255,255,255), 2)
        out.write(out_frame)

    if cv.waitKey(1) & 0xFF == ord('q'):
        break 
    
    # Update the target, in case the algorithm is in real-time
    #ea.update_target(img)
    #pso.update_target(img)

cv.destroyAllWindows()
out.release()

x = range(len(hbest))
plt.plot(x, hbest, c='r', label='best')
plt.legend()
plt.show()