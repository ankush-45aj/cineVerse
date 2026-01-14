// src/Component/CarouselSection.jsx
import React, { memo, useCallback } from 'react';
import Slider from 'react-slick';
import { useDispatch, useSelector } from 'react-redux';
import { openModal, recommendMoviesByName } from '../Store/Features/movieSlice';

const CarouselSection = ({ title, movies }) => {

  const dispatch = useDispatch();
  const statusRecommendedMoviesByName = useSelector(
    (state) => state.movie.statusRecommendedMoviesByName

  );
  const statusRecommendedMovies = useSelector(
    (state) => state.movie.statusRecommendedMovies

  );
  const statusMoviesTopRated = useSelector(
    (state) => state.movie.statusMoviesTopRated

  );
  const statusCatMovies = useSelector(
    (state) => state.movie.statusCatMovies

  );
  const statusRecord = useSelector(
    (state) => state.search.statusRecord
  );
  const settings = {
    dots: false,
    infinite: false,
    speed: 500,
    slidesToShow: 5,
    slidesToScroll: 5,
    responsive: [
      {
        breakpoint: 1024,
        settings: {
          slidesToShow: 3,
          slidesToScroll: 3,
        }
      },
      {
        breakpoint: 600,
        settings: {
          slidesToShow: 2,
          slidesToScroll: 2,
        }
      }
    ]
  };


  const handleMovieClick = useCallback((movie) => {
    dispatch(openModal(movie));
    if (statusRecommendedMoviesByName === "idle" || statusRecommendedMoviesByName === "succeeded") {
      if (movie) {
        dispatch(
          recommendMoviesByName({
            movieName: movie.movie_title
          })
        );
      }
    }
  }, []);

  return (
    <div className="py-8">
      {/* FIX: Removed {movies.movie_title} because 'movies' is a collection, not a single movie */}
      <h2 className="text-2xl text-white mb-4">{title}</h2>

      {statusRecommendedMoviesByName === 'pending' ||
        statusMoviesTopRated === "pending" ||
        statusCatMovies === "pending" ||
        statusRecommendedMovies === "pending" ? (
        <LoadingSkeleton />
      ) : (
        <Slider {...settings}>
          {/* FIX: Use Optional Chaining and ensure movies is not null */}
          {movies && Object.values(movies).map((movie, index) => (
            <div
              key={index}
              className="px-2 cursor-pointer"
              onClick={() => handleMovieClick(movie)}
            >
              <img
                src={movie?.poster_url || "https://m.media-amazon.com/images/M/MV5BMjIyNjkxNzEyMl5BMl5BanBnXkFtZTYwMjc3MDE3._V1_SX300.jpg"}
                alt={movie?.movie_title}
                className="w-full h-auto aspect-[2/3] object-cover rounded"
              />
              {/* Note: In your CSV dataset, the column is usually 'movie_title', not 'title' */}
              <p className="mt-2 text-sm text-white truncate">
                {movie?.movie_title || movie?.title}
              </p>
            </div>
          ))}
        </Slider>
      )}
    </div>
  );
};

export default CarouselSection;
